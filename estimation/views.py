from django.shortcuts import render
from datetime import datetime
import json
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.contrib.auth import authenticate
from django.db import connection, connections
from django.db.models import Count
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

#Some cache and decorator methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Create your views here.
from .permissions import ViewByStaffOnlyPermission
#models imports
from estimation.models import EstItemtypemaster,Papermasterfull
from estimation.models import EstProcessInputDetail
from estimation.models import FrontendResponse
#- save models
from estimation.models import EstGrainDirection
from estimation.models import EstBoard
from estimation.models import EstQty
from estimation.models import EstAdvanceInputDetail
from estimation.models import EstDimensions

from estimation.models import EstPrint
from estimation.models import EstCoating
from estimation.models import EstMetpetp
from estimation.models import EstLamination
from estimation.models import EstFoiling
from estimation.models import EstLinerBag
from estimation.models import EstPunching
from estimation.models import EstEmbossing
from estimation.models import EstPasting
from estimation.models import EstWindowPatching
from estimation.models import EstCorrugation
from estimation.models import EstFolding
from estimation.models import EstSorting
from estimation.models import EstBbp
from estimation.models import EstNewQuote
from estimation.models import PapergridQtyP



#serializers imports
from estimation.serializers import EstItemtypemasterSerializer
from estimation.serializers import InputDetailSerializer
from estimation.serializers import  FrontendResponseSerializer
from estimation.serializers import  ProcessInputSerializer
from estimation.serializers import  EstAdvanceInputDetailSerializer
from estimation.serializers import  EstNewQuoteSerializer
from estimation.serializers import  PaperGridQtyPSerializer

#From another App
from accounts.helpers import GetUserData

#private methods
from .helpers import  process_dropdown_data

class EstimationHome(APIView):
    """
    EstimationHome view accessible only to authenticated users.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    @swagger_auto_schema(
        operation_summary="Estimation App - Get the Item Masters and other data . ",
        operation_description="Retrieves type of cartons information for the authenticated user.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Estimation']
    )
    def get(self, request):
        try:
            #Fetch from EstItemtypemaster model
            queryset = EstItemtypemaster.objects.prefetch_related('itemtypedetail_set').all()
            serializer = EstItemtypemasterSerializer(queryset, many=True)

            #fetch from EstAdvanceInputDetail model
            advance_queryset = EstAdvanceInputDetail.objects.filter(isactive=True).order_by('seqno')
            advance_serializer = EstAdvanceInputDetailSerializer(advance_queryset, many=True)
            response_data = {
                "message": "Success",
                "data": {
                    "qm_response": serializer.data,
                    "advance_response": advance_serializer.data
                }
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Failed to fetch Estimation information: {str(e)}"
            return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class papermaster_boards(APIView):
    """
    Paper Master Board List view accessible only to authenticated users.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    @swagger_auto_schema(
        operation_summary="Estimation App - Get the Paper Master all data .",
        operation_description="Retrieves type of cartons information for the authenticated user.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Estimation']
    )
    def get(self, request):
        try:
            queryset = Papermasterfull.objects.filter(isactive=1)
            paper_data = {}
            for paper in queryset:
                manucompany = paper.manucompany
                paperkind = paper.paperkind
                gsm = paper.gsm
                if manucompany not in paper_data:
                    paper_data[manucompany] = {}
                if paperkind not in paper_data[manucompany]:
                    paper_data[manucompany][paperkind] = set()
                paper_data[manucompany][paperkind].add(gsm)
            return Response({
                "message": "Success",
                "data": paper_data
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            error_message = f"Failed to fetch paper data: {str(e)}"
            return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstProcessInputDetailList(APIView):
    """
    Estimation process input details List view accessible only to authenticated users.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    @swagger_auto_schema(
        operation_summary="Estimation App - Get the all process data .",
        operation_description="Retrieves process information witn nested json information for the authenticated user.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Estimation']
    )
    def get(self, request):
        try:
            # queryset = Papermasterfull.objects.filter(isactive=1)
            # queryset = EstProcessInputDetail.objects.filter(isactive=1)
            # serializer = InputDetailSerializer(queryset, many=True)

            queryset = EstProcessInputDetail.objects.filter(isactive=1)
            """
            # prid_data = {}
            for item in queryset:
                prid = item.prid
                serializer = InputDetailSerializer(item)
                # Append the serialized data to the corresponding prid key
                if prid in prid_data:
                    prid_data[prid].append(serializer.data)
                else:
                    prid_data[prid] = [serializer.data]"""
            queryset = EstProcessInputDetail.objects.filter(isactive=1)
            prid_data = self.process_input_details(queryset)
            return Response({
                "message": "Success",
                "data": prid_data
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            error_message = f"Failed to fetch paper data: {str(e)}"
            return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def process_input_details(self, queryset):
        prid_data = {}
        for item in queryset:
            prid = item.prid
            serializer = InputDetailSerializer(item)
            query_mapping = {
                "Complexcity": "SELECT ID, Name AS Complexcity FROM est_jobcomplexity WHERE PrID = %s AND IsActive = 1 ORDER BY Isdefault ASC",
                "Film Type": "SELECT a.LamID, CONCAT(a.FilmType, ' ', a.Micron, ' Micron') AS FilmType FROM lammetpetmaster AS a;",
                "Front/Back": "SELECT ID, `Description` FROM est_front_back AS a ORDER BY description DESC;",
                "Type": "SELECT CoatingID, Description FROM coating_master AS a WHERE isactive = 1 ORDER BY description ASC;",
                "Kind": "SELECT a.ID, Description FROM est_coating_kind AS a ORDER BY SeqNo ASC;",
                "Foil Film": "SELECT a.FoilID, a.Foiltype FROM foilmaster AS a;",
                "Lamination Film": "SELECT a.FoilID, a.Foiltype FROM foilmaster AS a;",
                "Lamination Type": "SELECT ID, Description FROM est_lam_kind AS a ORDER BY SeqNo ASC;",
                "Embose Type": "SELECT TypeID, Typedescription FROM item_embosetype_master AS a WHERE Isactive = 1;",
                "Pasting Type": "SELECT PastingID, Narration FROM pastingmaster AS a WHERE Inuse = 1;",
                "Window Film": "SELECT WPatchID, CONCAT(FilmType, ' ', Micron, ' Micron') FROM winpatchingmaster AS a WHERE IsActive = 1;",
                "Liner": "SELECT LinerID, CONCAT(LinerDesc, ' ', ROUND(LinerGsm, 0), ' GSM') FROM linermaster AS a WHERE IsActive = 1;",
                "Kraft GSM And Kind": "SELECT DISTINCT CorrPaperID, CONCAT(CorrPaperType, ' ', CorrGSM, ' GSM ', FLOOR(BurstFactor), ' BF') FROM corrpapermaster;",
                "Process Name": "SELECT CostID, PName FROM extracostmaster WHERE CostCretria = 'C';",
                "Gumming/Taping": "SELECT CostID, PName FROM extracostmaster WHERE CostCretria = 'C';",
                "Style": "SELECT SortID, Narration FROM sortingmasternew AS a WHERE inuse = 1;"
                # Add more queries for additional input label names
            }

            if item.input_label_name in query_mapping:
                query = query_mapping[item.input_label_name]
                if item.input_label_name == "Complexcity":
                    serialized_data = process_dropdown_data(serializer, query, prid)
                else:
                    serialized_data = process_dropdown_data(serializer, query)
                prid_data.setdefault(prid, []).append(serialized_data)
            else:
                prid_data.setdefault(prid, []).append(serializer.data)

        # Convert values to lists
        prid_data = {key: [value] for key, value in prid_data.items()}
        return prid_data
    """
    #use this for optional
    def process_input_details(self, queryset):
        prid_data = {}
        for item in queryset:
            prid = item.prid
            serializer = InputDetailSerializer(item)
            
            # Process input details based on input label name
            #We can add only one funtion for all the queries . Just pass the queries in the function.
            if item.input_label_name == "Complexcity":
                # serialized_data = self.process_complexcity(serializer, prid)
                query = "SELECT ID, Name AS Complexcity FROM est_jobcomplexity WHERE PrID = %s AND IsActive = 1 ORDER BY Isdefault ASC"
                params = [prid]
                serialized_data = process_dropdown_data(serializer,query,params)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Film Type":
                # serialized_data = self.process_filmtype(serializer, prid)
                query = "SELECT a.LamID,CONCAT(a.FilmType,' ',a.Micron, ' Micron') AS FilmType FROM lammetpetmaster AS a;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Front/Back":
                # serialized_data = self.process_Front_or_Back(serializer, prid)
                query = "SELECT  ID,`Description`  FROM est_front_back AS a ORDER BY description DESC ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Type":
                # serialized_data = self.process_Type(serializer, prid)
                query = "SELECT  CoatingID,Description  FROM coating_master AS a WHERE isactive = 1 ORDER BY description ASC ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Kind":
                # serialized_data = self.process_kind(serializer, prid)
                query = "SELECT  a.ID,Description  FROM est_coating_kind AS a  ORDER BY SeqNo ASC ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Foil Film":
                # serialized_data = self.process_foilfilm(serializer, prid)
                query = "SELECT  a.FoilID,a.Foiltype  FROM foilmaster AS a ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Lamination Film":
                # serialized_data = self.process_laminationfilm(serializer, prid)
                query = "SELECT  a.FoilID,a.Foiltype  FROM foilmaster AS a ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Lamination Type":
                # serialized_data = self.process_laminationtype(serializer, prid)
                query = "SELECT a.ID,a.Description   FROM est_lam_kind AS a ORDER BY SeqNo ASC ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Embose Type":
                # serialized_data = self.process_embosetype(serializer, prid)
                query = "SELECT a.TypeID,Typedescription   FROM item_embosetype_master AS a WHERE Isactive = 1 ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Pasting Type":
                # serialized_data = self.process_pastingtype(serializer, prid)
                query = "SELECT a.PastingID,a.Narration   FROM pastingmaster AS a WHERE Inuse = 1 ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Wimdow Film":
                # serialized_data = self.process_windowfilm(serializer, prid)
                query = "SELECT WPatchID,CONCAT(FilmType,' ',Micron,' Micron')   FROM winpatchingmaster AS a WHERE IsActive = 1 ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Liner":
                # serialized_data = self.process_liner(serializer, prid)
                query = "SELECT LinerID,CONCAT(LinerDesc,' ',ROUND(LinerGsm ,0),' GSM')   FROM linermaster AS a WHERE IsActive = 1;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Kraft GSM And Kind":
                # serialized_data = self.process_kraft_gsm_kind(serializer, prid)
                query = "SELECT DISTINCT CorrPaperID , (CONCAT(CorrPaperType,' ', CorrGSM,' GSM ', FLOOR(BurstFactor),' BF')) FROM `corrpapermaster` ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Process Name":
                # serialized_data = self.process_process_name(serializer, prid)
                query = "SELECT CostID,PName  FROM extracostmaster WHERE CostCretria = 'C';"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Gumming/Taping":
                # serialized_data = self.process_gumming_taping(serializer, prid)
                query = "SELECT CostID,PName  FROM extracostmaster WHERE CostCretria = 'C';"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Style":
                # serialized_data = self.process_style(serializer, prid)
                query = "SELECT a.SortID,a.Narration  FROM sortingmasternew AS a WHERE inuse = 1 ;"
                serialized_data = process_dropdown_data(serializer,query)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]

                    
            # elif:pass -  add the more label names in it.
            else:
                # Add serialized data to the corresponding prid key
                if prid in prid_data:
                    prid_data[prid].append(serializer.data)
                else:
                    prid_data[prid] = [serializer.data]
        # for key in prid_data:
        #     prid_data[key] = [prid_data[key]]
        prid_data = {key: [value] for key, value in prid_data.items()}
        return prid_data
    





    #this below functions are not used !
    def process_complexcity(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT ID, Name AS Complexcity FROM est_jobcomplexity WHERE PrID = %s AND IsActive = 1 ORDER BY Isdefault ASC", [prid])
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()    
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_filmtype(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT a.LamID,CONCAT(a.FilmType,' ',a.Micron, ' Micron') AS FilmType FROM lammetpetmaster AS a;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_Front_or_Back(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT  ID,`Description`  FROM est_front_back AS a ORDER BY description DESC ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_Type(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT  CoatingID,Description  FROM coating_master AS a WHERE isactive = 1 ORDER BY description ASC ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_kind(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT  a.ID,Description  FROM est_coating_kind AS a  ORDER BY SeqNo ASC ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_foilfilm(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT  a.FoilID,a.Foiltype  FROM foilmaster AS a ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list        
        return serialized_data
    def process_laminationfilm(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT  a.FoilID,a.Foiltype  FROM foilmaster AS a ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_laminationtype(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT a.ID,a.Description   FROM est_lam_kind AS a ORDER BY SeqNo ASC ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list        
        return serialized_data
    def process_embosetype(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT a.TypeID,Typedescription   FROM item_embosetype_master AS a WHERE Isactive = 1 ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_pastingtype(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT a.PastingID,a.Narration   FROM pastingmaster AS a WHERE Inuse = 1 ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_windowfilm(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT WPatchID,CONCAT(FilmType,' ',Micron,' Micron')   FROM winpatchingmaster AS a WHERE IsActive = 1 ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_liner(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT LinerID,CONCAT(LinerDesc,' ',ROUND(LinerGsm ,0),' GSM')   FROM linermaster AS a WHERE IsActive = 1;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_kraft_gsm_kind(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT CorrPaperID , (CONCAT(CorrPaperType,' ', CorrGSM,' GSM ', FLOOR(BurstFactor),' BF')) FROM `corrpapermaster` ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_process_name(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT CostID,PName  FROM extracostmaster WHERE CostCretria = 'C';")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list  
        return serialized_data
    def process_gumming_taping(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT CostID,PName  FROM extracostmaster WHERE CostCretria = 'C';")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    def process_style(self, serializer, prid):
        cursor = connection.cursor()
        cursor.execute("SELECT a.SortID,a.Narration  FROM sortingmasternew AS a WHERE inuse = 1 ;")
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        serialized_data['dropdown_list'] = dropdown_list
        return serialized_data
    

    #currently this is not used . Remove this comment after use of this function . 
    def perform_queries_(self,serializer,prid,queries,response_name=None):
        cursor = connection.cursor()
        cursor.execute(queries, [prid])
        dropdown_data = cursor.fetchall()
        dropdown_list = [{"complexcity": row[1], "value": row[0]} for row in dropdown_data]
        cursor.close()
        serialized_data = serializer.data
        if not response_name:
            serialized_data['dropdown_list'] = dropdown_list
        else:
            #only add it when you added the same in the serializer
            serialized_data[response_name] = dropdown_list        
        return serialized_data

    """


class ProcessInputView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    """
    Process Input Data.

    This endpoint receives input data from the frontend and saves or updates it.
    """

    @swagger_auto_schema(
        operation_summary="Process Input Data.",
        operation_description="Save or update process input data received from the frontend.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'grain_direction': openapi.Schema(type=openapi.TYPE_STRING),
                'quantity': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        format=openapi.FORMAT_INT32,
                        minimum=0,
                        description='List of quantities'
                    ),
                    required=['quantity'],
                    description='Array of quantities'
                ),
                'dimensions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'label_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'value': openapi.Schema(type=openapi.TYPE_STRING),
                        },
                        required=['label_name', 'value']
                    )
                ),
                'board_details': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'board_menufac': openapi.Schema(type=openapi.TYPE_STRING),
                            'board_type': openapi.Schema(type=openapi.TYPE_STRING),
                            'gsm': openapi.Schema(type=openapi.TYPE_STRING),
                            'BoardID': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        },
                        required=['board_menufac', 'board_type', 'gsm']
                    )
                ),
                'processes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'prid': openapi.Schema(type=openapi.TYPE_STRING),
                                    'sp_process_no': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'value': openapi.Schema(type=openapi.TYPE_STRING),
                                    'unique_name': openapi.Schema(type=openapi.TYPE_STRING),
                                },
                                required=['id', 'prid', 'sp_process_no', 'value', 'unique_name']
                            )
                        )
                    )
                ),
                'adv_options': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'unique_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'value': openapi.Schema(type=openapi.TYPE_STRING),
                        },
                        required=['unique_name', 'value']
                    ),
                    description='Array of advanced options'
                )
            },
            required=['grain_direction', 'quantity', 'dimensions', 'board_details', 'processes', 'adv_options']
        ),
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: 'Data processed successfully',
            400: 'Invalid input data',
            401: 'Unauthorized: Invalid access token',
            404: 'Not Found',
            500: 'Failed to process the data. Please try again later.'
        },
        tags=['Estimation']
    )
    
    def post(self, request, *args, **kwargs):
            try:
                serializer = ProcessInputSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)


                # Extract validated data
                validated_data = serializer.validated_data
                #EstNewQuote 
                user = GetUserData.get_user(request)
                auid = user.id
                icompanyid = user.icompanyid
                quotedate = datetime.now().strftime('%Y-%m-%d')[:10]
                adatetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                data = request.data
                client_name = data.get('Client_Name')
                product_name = data.get('Product_Name')
                product_code = data.get('Product_Code')
                carton_type_id = data.get('Carton_Type_ID')
                muid = data.get('MUID')
                mdatetime = data.get('MDateTime')
                remarks = data.get('Remarks')
                order_status = data.get('OrderStatus')
                is_active = data.get('IsActive')
                final_by = data.get('FinalBy')
                enq_no = data.get('EnqNo')
                doc_notion = data.get('DocNotion')
                est_notion = data.get('EstNotion')
                final_date = data.get('FinalDate')
                rep_id = data.get('RepID')
                impexp_status = data.get('ImpExpStatus')
                rev_quote_no = data.get('RevQuoteNo')
                grain_style = data.get('GrainStyle')
                location_id = data.get('LocationID')
                currency_id = data.get('CurrencyID')
                currency_factor = data.get('Currency_Factctor')
                currency_curr_amt = data.get('Currency_CurrAmt')
                client_category_id = data.get('ClientCategoryID')
                calculated_rate = data.get('CalculatedRate')
                quote_rate = data.get('QuoteRate')
                final_rate = data.get('FinalRate')
                fpid = data.get('FPID')

                adv_options=data.get('adv_options')
                field_mapping = {option['unique_name']: option['value'] for option in adv_options}

                # Now you can access the values using the unique_name as the key
                clientid = field_mapping.get('Client_Name_Drp')
                client_name = field_mapping.get('Client_Name')
                repid = field_mapping.get('Our_Executive')
                grainstyle = field_mapping.get('Grain_Style')
                currencyid = field_mapping.get('CurrancyID')
                


                new_quote = EstNewQuote(
                icompanyid=icompanyid,
                auid=auid,quotedate=quotedate,adatetime=adatetime,
                mdatetime=mdatetime,clientid=clientid,client_name=client_name,
                repid=repid,grainstyle=grainstyle,currencyid=currencyid,

                    # To Add more fields
                )
                new_quote.save(request=request)
                quoteid = new_quote.quoteid

                #End Est New Quote



                #grain_direction
                grain_direction = validated_data.get('grain_direction')
                # quoteid = 125
                _ = EstGrainDirection.objects.create(grain_direction=grain_direction,quoteid=quoteid)


                #board_details
                board_details = validated_data.get('board_details')
                # for key in validated json :
                #     perform looped action # This is for future use .
                for board_data in board_details:
                    _ = EstBoard.objects.create(
                        quoteid=quoteid,
                        boardid=board_data.get('BoardID'),
                        board_menufac=board_data.get('board_menufac'),
                        board_type=board_data.get('board_type'),
                        board_gsm=board_data.get('gsm'))
                # End board_details

                # Quantity
                quantities = validated_data.get('quantity')
                for qty in quantities:
                    _= EstQty.objects.create(quoteid=quoteid, qtyreq=qty)
                # End Quantity

                # Dimensions
                dimensions = validated_data.get('dimensions')
                for dim_data in dimensions:
                    _ = EstDimensions.objects.create(
                        quoteid=quoteid,
                        dimension_id=dim_data.get('label_name'),
                        dimension_value=dim_data.get('value'))
                    
                # End Dimensions

                #processes
                # This data not validated through seriliazer   . 
                processes = request.data.get('processes')
                processes = [item for sublist in processes for item in sublist]
                for process_list in processes:
                    final_data = {'quoteid': quoteid}
                    for process_data in process_list:
                        process_data = {key: value for key, value in process_data.items() if key not in ['id', 'prid', 'sp_process_no']}
                        process_data = {process_data['unique_name'].lower(): process_data['value']}
                        final_data.update(process_data)
                    for process_data in process_list:
                        prid = process_data['prid']
                        if prid == 'Pr':
                            model = EstPrint
                        elif prid == 'FC':
                            model = EstCoating
                        elif prid == 'FF':
                            model = EstFoiling
                        elif prid == 'FL':
                            model = EstLamination
                        elif prid == '39':
                            model = EstLinerBag
                        elif prid == 'PN':
                            model = EstPunching
                        elif prid == 'EM':
                            model = EstEmbossing
                        elif prid == 'Pa':
                            model = EstPasting
                        elif prid == 'WP':
                            model = EstWindowPatching
                        elif prid == 'FM':
                            model = EstCorrugation
                        elif prid == 'FO':
                            model = EstFolding
                        elif prid == 'BBP':
                            model = EstBbp
                        elif prid == 'SO':
                            model = EstSorting
                        else:
                            #remove this - 
                            model = None
                        if model !=None :
                            try:
                                model.objects.create(**final_data)
                            except Exception as e:
                                # Handle exceptions (e.g., validation errors)
                                print(f"Failed to insert data into {model.__name__}: {e}")
                        break

                # End Processes

                # Run the procedure
                args = ['', 1, 0, 4, 0, 31, 31, 67, 7, 10, 0, 0, 0, 0, 0, 0, 5, 5, 5, 10]
                with connection.cursor() as cursor:
                    cursor.callproc('RND_CartonPlanning', args)
                    results = {}
                    table_index = 1
                    while True:
                        rows = cursor.fetchall()
                        if not rows:
                            break
                        column_names = [desc[0] for desc in cursor.description]
                        results[f"table_{table_index}"] = [dict(zip(column_names, row)) for row in rows]
                        cursor.nextset()
                        table_index += 1

                    
                return Response({"message": "Data processed successfully", "data": {"quote_id": new_quote.quoteid ,"cs_response":results} }, status=status.HTTP_200_OK)
            except ValidationError as e:
                error_message = "Invalid input data"
                return Response({"message": error_message, "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                error_message = f"Failed to fetch/save Process Input View information: {str(e)}"
                return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaperGridQtyAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    """
    API endpoint for processing input data and fetching Paper Grid information.
    """
    @swagger_auto_schema(
        operation_summary="Process input data and fetch Paper Grid information.",
        operation_description="This endpoint processes the input data, which includes a comma-separated list of Inc values, and fetches Paper Grid information based on the provided Inc values.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'inc_data': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Comma-separated list of Inc values like "3325, 3334, ..." '
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: "Success",
            400: "Bad Request",
            500: "Internal Server Error"
        },
        tags=['Estimation']
    )
    def post(self, request, *args, **kwargs):
        try:
            inc_data = request.data.get('inc_data')
            if not inc_data:
                return Response({'error': 'inc_data parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            inc_ids = [int(inc_id) for inc_id in inc_data.split(',')]
            paper_grid_data = PapergridQtyP.objects.filter(inc__in=inc_ids).values('inc', 'dackle_dim', 'grain_dim', 'ups', 'areapercarton_sqinch', 'scan', 'grain', 'machineid', 'machinename', 'noofpass_req', 'mat_x', 'mat_y', 'dielength_in_inch', 'qty', 'f_color', 'b_color', 'die_planheight', 'die_planwidth', 'fullsheet_d', 'fullsheet_g', 'fullsheet_grain', 'fullsheet_cut_x', 'fullsheet_cut_y', 'fullsheet_ups', 'sheets_a', 'heightcut', 'widthcut', 'lengthremaining', 'widthremaining', 'itemsinfirstcut', 'totalcuts', 'totalbox', 'dackle_dim_b', 'grain_dim_b', 'ups_b', 'mat_x_b', 'mat_y_b', 'cuts_b', 'sheets_b', 'dackle_dim_c', 'grain_dim_c', 'ups_c', 'mat_x_c', 'mat_y_c', 'cuts_c', 'sheets_c', 'dackle_dim_d', 'grain_dim_d', 'ups_d', 'mat_x_d', 'mat_y_d', 'cuts_d', 'sheets_d', 'dackle_dim_tot', 'grain_dim_tot', 'wastage_x', 'wastage_y', 'wastage_weight_kg_a', 'wastage_weight_kg_b', 'wastage_weight_kg', 'utilizationper', 'fullsheet_req', 'paperid', 'gsm', 'paper_rate', 'paper_unit', 'print_size_sheets', 'print_impression', 'paper_kg', 'paper_kg_fullsheet', 'paper_amt', 'punchdie_amt', 'plate_amt', 'prmake_ready_amt', 'printing_amt', 'total_amt', 'pn_mcid', 'pn_machinename', 'pn_maxdackle', 'pn_mindackle', 'pn_maxgrain', 'pn_mingrain', 'pn_gripper', 'pn_makerdy_amt', 'pn_punching_amt')
            serializer = PaperGridQtyPSerializer(paper_grid_data, many=True)
            return Response({"message": "Data Fetched successfully", "data": serializer.data }, status=status.HTTP_200_OK)
        except Exception as e:
                error_message = f"Failed to fetch Paper GridQty APIView information: {str(e)}"
                return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Costsheet(APIView):
    """
    API endpoint to process cost sheet data.
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Process Cost Sheet Data.",
        operation_description="Executes the RND_CartonPlanning stored procedure with the provided parameters.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recordID': openapi.Schema(type=openapi.TYPE_STRING, description="Record ID."),
                'TabNo': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tab Number.")
            },
            required=['recordID', 'TabNo']
        ),
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: openapi.Response(description='Data processed successfully'),
            400: openapi.Response(description='Invalid input data'),
            401: openapi.Response(description='Unauthorized: Invalid access token'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Failed to process the data. Please try again later.')
        },
        tags=['Estimation']
    )
    def post(self, request, *args, **kwargs):
        """
        Execute the RND_CartonPlanning stored procedure with the provided parameters.
        
        Args:
            request (Request): The incoming HTTP request containing the parameters.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the processed data or an error message.
        """
        try:
            record_id = request.data.get('recordID')
            tab_no = request.data.get('TabNo')
            
            with connection.cursor() as cursor:
                # cursor.execute("SELECT * FROM qcsheetex1 WHERE recordID=%s AND TabNo=%s ORDER BY CAST(field8 AS DECIMAL)", [record_id, tab_no])
                cursor.execute("SELECT * FROM qcsheetex1 WHERE recordID=%s AND TabNo=%s ORDER BY CAST(rowno AS DECIMAL);", [record_id, tab_no])
                results = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in results]
                
            return Response({"message": "success. ", "data": data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            error_message = f"Failed to process the data: {str(e)}"
            return Response({"message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes for whole view
class EstNewQuoteListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    # you can set this to user role wise .

    @swagger_auto_schema(
        operation_summary="Retrieve all quote .",
        operation_description="Fetch all the quotes which saved by the logged user .",
        
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            200: 'Data processed successfully',
            400: 'Invalid input data',
            401: 'Unauthorized: Invalid access token',
            404: 'Not Found',
            500: 'Failed to process the data. Please try again later.'
        },
        tags=['Estimation']
    )
    
    @method_decorator(cache_page(60 * 1))
    def get(self, request, *args, **kwargs):
        """
        Retrieve all quotes associated with the provided user ID.

        Args:
            request (Request): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Response containing the serialized list of quotes or an error message.
        """
        try:
            auid = request.user.id
            user = GetUserData.get_user(request)
            if auid and (user.is_superuser):
                # If admin or superuser, fetch all quotes
                quotes = EstNewQuote.objects.all()
            else:
                # Otherwise, filter quotes based on the logged-in user
                quotes = EstNewQuote.objects.filter(auid=auid) #By the logged User .

            serializer = EstNewQuoteSerializer(quotes, many=True)
            return Response({"message": "Data fetched successfully", "data": serializer.data }, status=status.HTTP_200_OK)
        except EstNewQuote.DoesNotExist:
            return Response({"message": "Quotes not found", "data": {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                error_message = f"Failed to fetch Estimations : {str(e)}"
                return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
    operation_summary="Update the Quote.",
    operation_description="Update the existing quote with the provided data.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'quote_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the quote to be updated.'
            ),
            'quotedate': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Quote date.'
            ),
            'quote_no': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Quote number.'
            ),
            'icompanyid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Company ID.'
            ),
            'clientid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Client ID.'
            ),
            'client_name': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Client name.'
            ),
            'product_name': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Product name.'
            ),
            'product_code': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Product code.'
            ),
            'carton_type_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Carton type ID.'
            ),
            'auid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='AUID.'
            ),
            'adatetime': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='AUID date time.'
            ),
            'muid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='MUID.'
            ),
            'mdatetime': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='MUID date time.'
            ),
            'remarks': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Remarks.'
            ),
            'orderstatus': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Order status.'
            ),
            'isactive': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Is active.'
            ),
            'finalby': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Final by.'
            ),
            'enqno': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Enquiry number.'
            ),
            'docnotion': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Doc notion.'
            ),
            'estnotion': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Estimation notion.'
            ),
            'finaldate': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Final date.'
            ),
            'repid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Representative ID.'
            ),
            'impexpstatus': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Import/export status.'
            ),
            'revquoteno': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Revised quote number.'
            ),
            'grainstyle': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Grain style.'
            ),
            'locationid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Location ID.'
            ),
            'currencyid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Currency ID.'
            ),
            'currency_factctor': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Currency factor.'
            ),
            'currency_curramt': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Currency current amount.'
            ),
            'clientcategoryid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Client category ID.'
            ),
            'calculatedrate': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Calculated rate.'
            ),
            'quoterate': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Quote rate.'
            ),
            'finalrate': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Final rate.'
            ),
            'fpid': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='FPID.'
            ),
        },
        required=['quote_id']
    ),
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            description='Bearer token',
            required=True,
            format='Bearer <Token>'
        )
    ],
    responses={
        200: 'Data updated successfully',
        400: 'Invalid input data',
        401: 'Unauthorized: Invalid access token',
        404: 'Not Found',
        500: 'Failed to process the data. Please try again later.'
    },
    tags=['Estimation']
    )

    def patch(self, request, *args, **kwargs):
        try:
            quote_id = request.data.get('quote_id')
            quote = EstNewQuote.objects.get(quoteid=quote_id)
            serializer = EstNewQuoteSerializer(quote, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(request=request) #for signal
                return Response({"message": "Data updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid input data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except EstNewQuote.DoesNotExist:
            return Response({"message": "Quote not found", "data": {}}, status=status.HTTP_404_NOT_FOUND)



    @swagger_auto_schema(
        operation_summary="Delete the Quote .  .",
        operation_description="You can delete the Estimation from the list by passing quoteid .",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quote_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Dict of quote_id .'
                )
            },
            required=['quote_id']
        ),
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        responses={
            204: 'Data Deleted successfully',
            400: 'Invalid input data',
            401: 'Unauthorized: Invalid access token',
            404: 'Not Found',
            500: 'Failed to process the data. Please try again later.'
        },
        tags=['Estimation']
    )
    def delete(self, request, *args, **kwargs):
        """
        Delete a specific quote from the system.

        Args:
            request (Request): The incoming HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Request Body:
            {
                'quote_id': int,  # ID of the quote to delete.
            }

        Returns:
            Response: Response indicating success or failure of the delete operation.
        """
        try:
            quote_id = request.data.get('quote_id')
            quote = EstNewQuote.objects.get(quoteid=quote_id)
            quote.delete(request=request)
            return Response({"message": "Data deleted successfully", "data": {} }, status=status.HTTP_204_NO_CONTENT)
        except EstNewQuote.DoesNotExist:
            return Response({"message": "Estimation not found", "data": {} }, status=status.HTTP_404_NOT_FOUND)
# change the payload json_response or the parsing method
# add all the tables
# parse all informations with dynamic like which contains foiling and what if someone not use foiling manage that payload optional
# Check the cost sheet