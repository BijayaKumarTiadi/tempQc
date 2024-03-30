from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
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
#serializers imports
from estimation.serializers import EstItemtypemasterSerializer
from estimation.serializers import InputDetailSerializer
from estimation.serializers import  FrontendResponseSerializer


#private methods
from .helpers import process_dropdown_data

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
            queryset = EstItemtypemaster.objects.prefetch_related('itemtypedetail_set').all()
            serializer = EstItemtypemasterSerializer(queryset, many=True)
            return Response({"message": "Success","data": serializer.data},status=status.HTTP_200_OK)
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
    """
    View to process input data from the frontend.

    This endpoint allows you to process input data received from the frontend.
    The input data should include a JSON response from the frontend.

    :param json_response: JSON response received from the frontend.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Process Input Data.",
        operation_description="saved and updates Process input data received from the frontend.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'json_response': openapi.Schema(type=openapi.TYPE_OBJECT)
            },
            required=['json_response']
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
    def post(self, request):
            try:
                # data = request.data
                quote_id = self.insert_into_est_new_quote(request)
                #- > here we will proceed further for the another functions which will save the other parse datas
                if quote_id:
                    self.insert_into_est_qty(request,quote_id)
                return Response({"message": "Data processed successfully", "data": {"quote_id": quote_id} }, status=status.HTTP_200_OK)
            except Exception as e:
                error_message = f"Failed to fetch/save Process Input View information: {str(e)}"
                return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_userid(self,request):
            try:
                header = request.headers.get('Authorization')
                parts = header.split()
                access_token = parts[1]
                access_token = AccessToken(access_token)
                user_id = access_token['user_id']
                return user_id
            except Exception as e:
                error_message = f"Failed to fetch user information for user id  : {str(e)}"
                return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def insert_into_est_new_quote(self, request):
        """
        Insert data into the Est_New_quote table.

        This function inserts data into the Est_New_quote table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record (QuoteID).
        :rtype: int
        """
        auid = self.get_userid(request)

        data = request.data
        quote_date  = datetime.now().strftime('%Y-%m-%d')[:10]
        ADateTime  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_id = data.get('ClientID')
        client_name = data.get('Client_Name')
        product_name = data.get('Product_Name')
        product_code = data.get('Product_Code')
        carton_type_id = data.get('Carton_Type_ID')
        remarks = data.get('Remarks')
        order_status = data.get('OrderStatus')
        is_active = data.get('IsActive')
        '''
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Est_New_quote 
                (QuoteDate, ClientID, Client_Name, Product_Name, Product_Code, Carton_Type_ID, AUID, Remarks, OrderStatus, IsActive)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [quote_date, client_id, client_name, product_name, product_code, carton_type_id, auid, remarks, order_status, is_active])
            quote_id = cursor.lastrowid  # Retrieve the last inserted ID
            return quote_id
        '''
        filtered_data = {
            'QuoteDate': quote_date,
            'ClientID': client_id,
            'Client_Name': client_name,
            'Product_Name': product_name,
            'Product_Code': product_code,
            'Carton_Type_ID': carton_type_id,
            'AUID': auid,
            'ADateTime': ADateTime,
            'Remarks': remarks,
            'OrderStatus': order_status,
            'IsActive': is_active
        }
        filtered_data = {k: v for k, v in filtered_data.items() if v is not None}
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(filtered_data))
            columns = ', '.join(filtered_data.keys())
            values = list(filtered_data.values())
            
            sql = f"""
                INSERT INTO Est_New_quote 
                ({columns})
                VALUES ({placeholders})
            """
            cursor.execute(sql, values)
            quote_id = cursor.lastrowid 
            return quote_id

    def insert_into_est_qty(self, request, quote_id):
        """
        Insert data into the Est_Qty table.

        This function inserts data into the Est_Qty table based on the provided request data and quote_id.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest
        :param quote_id: The ID of the quote to associate the quantities with.
        :type quote_id: int

        :return: None
        """
        try:
            quantities = request.data.get("quantity", [])
            print(f"Quantities to insert: {quantities}")
            with connection.cursor() as cursor:
                for quantity_data in quantities:
                    qty_req = quantity_data.get("quantity")
                    print(f"quote_id: {quote_id}, qty_req: {qty_req}")
                    cursor.execute(""" INSERT INTO Est_Qty (QuoteID, QtyReq) VALUES (%s, %s) ; """, (int(quote_id), int(qty_req)))
                print("Quantities inserted successfully.")
        except Exception as e:
            error_message = f"Failed to insert quantities into Est_Qty table: {str(e)}"
            print(error_message)
            #Handle the error appropriately, e.g., logging, returning error response, etc.
       

# change the payload json_response or the parsing method
# add all the tables
# parse all informations with dynamic like which contains foiling and what if someone not use foiling manage that payload optional
# Check the cost sheet