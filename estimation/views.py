from django.shortcuts import render
from datetime import datetime
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



#serializers imports
from estimation.serializers import EstItemtypemasterSerializer
from estimation.serializers import InputDetailSerializer
from estimation.serializers import  FrontendResponseSerializer
from estimation.serializers import  ProcessInputSerializer
from estimation.serializers import  EstAdvanceInputDetailSerializer


#From another App
from accounts.helpers import GetUserData

#private methods
from .helpers import  process_dropdown_data
from .helpers import insert_into_est_new_quote
from .helpers import insert_data_into_table
from .helpers import insert_into_est_qty

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
                )
            },
            required=['grain_direction', 'quantity', 'dimensions', 'board_details', 'processes']
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
                client_id = data.get('ClientID')
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
                


                new_quote = EstNewQuote(
                icompanyid=icompanyid,
                auid=auid,quotedate=quotedate,adatetime=adatetime,
                mdatetime=mdatetime,

                    # To Add more fields
                )
                new_quote.save()
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
                    print(final_data)
                    print("...........\n")
                # End Processes

                #Fetch the table data
                response = []
                with connection.cursor() as cursor:
                    cursor.callproc('RND_CartonPlanning', ['', 1, 0, 4, 0, 31, 31, 67, 7, 10, 0, 0, 0, 0, 0, 0, 5, 5, 5, 10])
                    columns = [col[0] for col in cursor.description]
                    for row in cursor.fetchall():
                        response.append({columns[i]: row[i] for i in range(len(columns))})
                    
                return Response({"message": "Data processed successfully", "data": {"quote_id": new_quote.quoteid ,"cs_response":response} }, status=status.HTTP_200_OK)
            except ValidationError as e:
                error_message = "Invalid input data"
                return Response({"message": error_message, "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                error_message = f"Failed to fetch/save Process Input View information: {str(e)}"
                return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Costsheet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Process Cost Sheet Data.",
        operation_description="Executes the RND_CartonPlanning stored procedure with the provided parameters.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'PMachineID': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the machine"),
                
            },
            required=['PMachineID']
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
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM qcsheetex1 WHERE recordID='00001' AND TabNo=0 ORDER BY CAST(field8 AS DECIMAL)")
                results = cursor.fetchall()  # Fetch all the results
                columns = [col[0] for col in cursor.description]  # Get column names
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))  # Create dictionary for each row
            return Response({"message": "Data processed successfully", "data": data }, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Failed to process the data: {str(e)}"
            return Response({"message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# change the payload json_response or the parsing method
# add all the tables
# parse all informations with dynamic like which contains foiling and what if someone not use foiling manage that payload optional
# Check the cost sheet