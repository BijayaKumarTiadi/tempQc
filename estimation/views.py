from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
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
#serializers imports
from estimation.serializers import EstItemtypemasterSerializer
from estimation.serializers import InputDetailSerializer
from estimation.serializers import  ProcessInputSerializer


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
            
            # Process input details based on input label name
            #We can add only one funtion for all the queries . Just pass the queries in the function.
            if item.input_label_name == "Complexcity":

                serialized_data = self.process_complexcity(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Film Type":
                serialized_data = self.process_filmtype(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Front/Back":
                serialized_data = self.process_Front_or_Back(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Type":
                serialized_data = self.process_Type(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Kind":
                serialized_data = self.process_kind(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Foil Film":
                serialized_data = self.process_foilfilm(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Lamination Film":
                serialized_data = self.process_laminationfilm(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Lamination Type":
                serialized_data = self.process_laminationtype(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Embose Type":
                serialized_data = self.process_embosetype(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Pasting Type":
                serialized_data = self.process_pastingtype(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Wimdow Film":
                serialized_data = self.process_windowfilm(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Liner":
                serialized_data = self.process_liner(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Kraft GSM And Kind":
                serialized_data = self.process_kraft_gsm_kind(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Process Name":
                serialized_data = self.process_process_name(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Gumming/Taping":
                serialized_data = self.process_gumming_taping(serializer, prid)
                if prid in prid_data:
                    prid_data[prid].append(serialized_data)
                else:
                    prid_data[prid] = [serialized_data]
            elif item.input_label_name == "Style":
                serialized_data = self.process_style(serializer, prid)
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
    

class ProcessInputView(APIView):
    """
    View to process input data from the frontend.

    This endpoint allows you to process input data received from the frontend.
    The input data should include quantity, dimensions, board_menufac, gsm, and processes.

    :param quantity: List of dictionaries containing quantity data.
    :param dimensions: List of dictionaries containing dimensions data.
    :param board_menufac: Board manufacturing details.
    :param board_type: Type of board.
    :param gsm: GSM (grams per square meter) of the board.
    :param processes: List of lists containing process details.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Process Input Data.",
        operation_description="Process input data received from the frontend.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quantity': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'quantity': openapi.Schema(type=openapi.TYPE_STRING)})
                ),
                'dimensions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'label_name': openapi.Schema(type=openapi.TYPE_STRING, description='Dimension label name'),
                            'default_value': openapi.Schema(type=openapi.TYPE_STRING, description='Default dimension value')
                        }
                    )
                ),
                'board_menufac': openapi.Schema(type=openapi.TYPE_STRING, description='Board manufacturing details'),
                'board_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of board'),
                'gsm': openapi.Schema(type=openapi.TYPE_STRING, description='GSM of the board'),
                'processes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Process ID'),
                                'prid': openapi.Schema(type=openapi.TYPE_STRING, description='PR ID'),
                                'sp_process_no': openapi.Schema(type=openapi.TYPE_INTEGER, description='Special process number'),
                                'input_default_value': openapi.Schema(type=openapi.TYPE_STRING, description='Input default value')
                            }
                        )
                    )
                )
            },
            required=['quantity', 'dimensions', 'board_menufac', 'board_type', 'gsm', 'processes']
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
        serializer = ProcessInputSerializer(data=request.data)
        if serializer.is_valid():
            processed_data = serializer.validated_data
            quantity_data = processed_data.get('quantity')
            board_menufac_data = processed_data.get('board_menufac')
            return Response({"message": "Data processed successfully", "data": processed_data}, status=status.HTTP_200_OK)
        else:
            # Return an error response if the input data is invalid
            return Response({"message": "Invalid input data", "errors": serializer.errors,'data':{}}, status=status.HTTP_400_BAD_REQUEST)
