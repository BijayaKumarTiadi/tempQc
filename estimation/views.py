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



'''
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
        # Vars not from the EndUser data
        auid = self.get_userid(request)
        quote_date = datetime.now().strftime('%Y-%m-%d')[:10]
        ADateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data = request.data
        company_id = data.get('ICompanyID')
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

        filtered_data = {
            'QuoteDate': quote_date,
            'ICompanyID': company_id,
            'ClientID': client_id,
            'Client_Name': client_name,
            'Product_Name': product_name,
            'Product_Code': product_code,
            'Carton_Type_ID': carton_type_id,
            'AUID': auid,
            'ADateTime': ADateTime,
            'MUID': muid,
            'MDateTime': mdatetime,
            'Remarks': remarks,
            'OrderStatus': order_status,
            'IsActive': is_active,
            'FinalBy': final_by,
            'EnqNo': enq_no,
            'DocNotion': doc_notion,
            'EstNotion': est_notion,
            'FinalDate': final_date,
            'RepID': rep_id,
            'ImpExpStatus': impexp_status,
            'RevQuoteNo': rev_quote_no,
            'GrainStyle': grain_style,
            'LocationID': location_id,
            'CurrencyID': currency_id,
            'Currency_Factctor': currency_factor,
            'Currency_CurrAmt': currency_curr_amt,
            'ClientCategoryID': client_category_id,
            'CalculatedRate': calculated_rate,
            'QuoteRate': quote_rate,
            'FinalRate': final_rate,
            'FPID': fpid
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
    def insert_into_est_board(self, request,quote_id):
        """
        Insert data into the Est_Board table.

        This function inserts data into the Est_Board table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record.
        :rtype: int
        """
        try:
            data = request.data
            #The all data here are optional
            board_id = data.get('BoardID')
            board_type = data.get('Board_Type')
            board_gsm = data.get('Board_GSM')

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Est_Board 
                    (QuoteID, BoardID, Board_Type, Board_GSM)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, [quote_id, board_id, board_type, board_gsm])
                board_id = cursor.lastrowid 
                return board_id
        except Exception as e:
            error_message = f"Failed to insert quantities into Est_Qty table: {str(e)}"
            print(error_message)
    def insert_into_est_metpetp(self, request,quote_id):
        """
        Insert data into the Est_Metpetp table.

        This function inserts data into the Est_Metpetp table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record.
        :rtype: int
        """
        try:
            data = request.data
            mp_ft = data.get('MP_FT')
            # its varchar 10 we need to filter that also
            mp_ft = mp_ft[:10] if mp_ft else None 
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Est_Metpetp 
                    (QuoteID, MP_FT)
                    VALUES (%s, %s)
                """
                cursor.execute(sql, [quote_id, mp_ft])
                metpetp_id = cursor.lastrowid 
                return metpetp_id
        except Exception as e:
            error_message = f"Failed to insert quantities into Est_Qty table: {str(e)}"
            print(error_message)
    def insert_into_est_print(self, request,quote_id):
        """
        Insert data into the Est_Print table.

        This function inserts data into the Est_Print table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record.
        :rtype: int
        """
        try:
            data = request.data
            pr_complex = data.get('Pr_Complex')
            pr_fcol = data.get('Pr_FCol')
            pr_fb = data.get('Pr_FB')
            pr_add_pl = data.get('Pr_Add_Pl')

            pr_fcol = data.get('Pr_FCol')
            if pr_fcol is None or not isinstance(pr_fcol, int) or not (0 <= pr_fcol <= 99):
                raise ValueError("Pr_FCol must be a non-null integer between 0 and 99")
            if pr_fb is None:
                raise ValueError("Pr_FB cannot be null")
            
            if pr_add_pl is None or not isinstance(pr_add_pl, int) or not (0 <= pr_add_pl <= 999):
                raise ValueError("Pr_Add_Pl must be a non-null integer between 0 and 999")

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Est_Print 
                    (QuoteID, Pr_Complex, Pr_FCol, Pr_FB, Pr_Add_Pl)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, [quote_id, pr_complex, pr_fcol, pr_fb, pr_add_pl])
                print_id = cursor.lastrowid 
                return print_id
        except Exception as e:
            error_message = f"Failed to insert quantities into Est_Qty table: {str(e)}"
            print(error_message)
    def insert_into_est_coating(self, request,quote_id):
        """
        Insert data into the Est_coating table.

        This function inserts data into the Est_coating table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record.
        :rtype: int
        """
        try:
            data = request.data
            fc_type = data.get('FC_Type')
            if fc_type is None:
                raise ValueError("FC_Type cannot be null")

            fc_kind = data.get('FC_Kind')
            if fc_kind is None:
                raise ValueError("FC_Kind cannot be null")

            fc_area = data.get('FC_Area')
            if fc_area is None:
                raise ValueError("FC_Area cannot be null")
            if not isinstance(fc_area, float):
                raise ValueError("FC_Area must be a float")
            
            fb = data.get('FB')
            if fb is None:
                raise ValueError("FB cannot be null")

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Est_coating 
                    (QuoteID, FC_Type, FC_Kind, FC_Area, FB)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, [quote_id, fc_type, fc_kind, fc_area, fb])
                coating_id = cursor.lastrowid 
                return coating_id
        except Exception as e:
            error_message = f"Failed to insert quantities into Est_Qty table: {str(e)}"
            print(error_message)
    def insert_into_est_lamination(self, request,quote_id):
        """
        Insert data into the Est_lamination table.

        This function inserts data into the Est_lamination table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record.
        :rtype: int
        """
        try:
            data = request.data
            fl_film = data.get('FL_Film')
            if fl_film is None:
                raise ValueError("FL_Film cannot be null")

            fl_type = data.get('FL_Type')
            if fl_type is None:
                raise ValueError("FL_Type cannot be null")

            fl_strips = data.get('FL_Strips')
            if fl_strips is None:
                raise ValueError("FL_Strips cannot be null")
            if not isinstance(fl_strips, int):
                raise ValueError("FL_Strips must be an integer")

            fb = data.get('FB')
            if fb is None:
                raise ValueError("FB cannot be null")

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Est_lamination 
                    (QuoteID, FL_Film, FL_Type, FL_Strips, FB)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, [quote_id, fl_film, fl_type, fl_strips, fb])
                lamination_id = cursor.lastrowid 
                return lamination_id
        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Error occurred: {str(e)}")
            return None
    def insert_into_est_foiling(self, request,quote_id):
        """
        Insert data into the Est_Foiling table.

        This function inserts data into the Est_Foiling table based on the provided request data.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest

        :return: The ID of the newly inserted record.
        :rtype: int
        """
        try:
            data = request.data
            ff_film = data.get('FF_Film')
            if ff_film is None:
                raise ValueError("FF_Film cannot be null")

            ff_l = data.get('FF_L')
            if ff_l is None:
                raise ValueError("FF_L cannot be null")
            if not isinstance(ff_l, float):
                raise ValueError("FF_L must be a floating-point number")

            ff_b = data.get('FF_B')
            if ff_b is None:
                raise ValueError("FF_B cannot be null")
            if not isinstance(ff_b, float):
                raise ValueError("FF_B must be a floating-point number")

            fb = data.get('FB')
            if fb is None:
                raise ValueError("FB cannot be null")

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Est_Foiling 
                    (QuoteID, FF_Film, FF_L, FF_B, FB)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, [quote_id, ff_film, ff_l, ff_b, fb])
                foiling_id = cursor.lastrowid 
                return foiling_id
        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Error occurred: {str(e)}")
            return None

'''


class ProcessInputView(APIView):
    """
        Process Input Data.

        This endpoint receives input data from the frontend and saves or updates it.

        Payload Structure:
        {
        "json_response": {
            "est_new_quote": {
            "Quote_No": "123456",
            "ICompanyID": "00001",
            "ClientID": "1001",
            "Client_Name": "Test Client",
            "Product_Name": "Test Product",
            "Product_Code": "PROD-001",
            "Carton_Type_ID": 123,
            "MUID": "M123",
            "MDateTime": "2060-01-01 01:01:01",
            "Remarks": "Test remarks",
            "OrderStatus": "Pending",
            "IsActive": 1,
            "FinalBy": "John Doe",
            "EnqNo": "ENQ-001",
            "DocNotion": 24,
            "EstNotion": "Est Notion",
            "FinalDate": "2060-01-01 01:01:01",
            "RepID": "R123",
            "ImpExpStatus": "I",
            "RevQuoteNo": 0,
            "GrainStyle": 0,
            "LocationID": "L456",
            "CurrencyID": "C1",
            "Currency_Factctor": 1.20,
            "Currency_CurrAmt": 10.00,
            "ClientCategoryID": "CC789",
            "CalculatedRate": 1200.25,
            "QuoteRate": 1100.75,
            "FinalRate": 1250.25,
            "FPID": "FP456"
            },
            "est_qty": [{"quantity":"10000"},{"quantity":"500"},{"quantity":"2000"}],
            "est_board": {
            "BoardID": "56456",
            "Board_Type": "Demo Type",
            "Board_GSM": 200
            },
            "est_metpetp": {
            "MP_FT": "Test Value"
            },
            "est_print": {
            "Pr_Complex": "Complex",
            "Pr_FCol": 1,
            "Pr_FB": "Test FB",
            "Pr_Add_Pl": 10
            },
            "est_coating": {
            "FC_Type": "Type Value",
            "FC_Kind": "Kind Value",
            "FC_Area": 50,
            "FB": "Test FB"
            },
            "est_lamination": {
            "FL_Film": "Film Value",
            "FL_Type": "Type Value",
            "FL_Strips": 2,
            "FB": "Test FB"
            },
            "est_foiling": {
            "FF_Film": "Film Value",
            "FF_L": 10.5,
            "FF_B": 5.25,
            "FB": "Test FB"
            }
        }
        }
    """
    @swagger_auto_schema(
        operation_summary="Process Input Data.",
        operation_description="Save or update process input data received from the frontend.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'json_response': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'est_new_quote': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "Quote_No": openapi.Schema(type=openapi.TYPE_STRING),
                                "ICompanyID": openapi.Schema(type=openapi.TYPE_STRING),
                                "ClientID": openapi.Schema(type=openapi.TYPE_STRING),
                                "Client_Name": openapi.Schema(type=openapi.TYPE_STRING),
                                "Product_Name": openapi.Schema(type=openapi.TYPE_STRING),
                                "Product_Code": openapi.Schema(type=openapi.TYPE_STRING),
                                "Carton_Type_ID": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "MUID": openapi.Schema(type=openapi.TYPE_STRING),
                                "MDateTime": openapi.Schema(type=openapi.TYPE_STRING),
                                "Remarks": openapi.Schema(type=openapi.TYPE_STRING),
                                "OrderStatus": openapi.Schema(type=openapi.TYPE_STRING),
                                "IsActive": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "FinalBy": openapi.Schema(type=openapi.TYPE_STRING),
                                "EnqNo": openapi.Schema(type=openapi.TYPE_STRING),
                                "DocNotion": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "EstNotion": openapi.Schema(type=openapi.TYPE_STRING),
                                "FinalDate": openapi.Schema(type=openapi.TYPE_STRING),
                                "RepID": openapi.Schema(type=openapi.TYPE_STRING),
                                "ImpExpStatus": openapi.Schema(type=openapi.TYPE_STRING),
                                "RevQuoteNo": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "GrainStyle": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "LocationID": openapi.Schema(type=openapi.TYPE_STRING),
                                "CurrencyID": openapi.Schema(type=openapi.TYPE_STRING),
                                "Currency_Factctor": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "Currency_CurrAmt": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "ClientCategoryID": openapi.Schema(type=openapi.TYPE_STRING),
                                "CalculatedRate": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "QuoteRate": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "FinalRate": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "FPID": openapi.Schema(type=openapi.TYPE_STRING)
                            },
                            required=[
                                "Quote_No",
                                "ICompanyID",
                                "ClientID",
                                "Client_Name",
                                "Product_Name",
                                "Product_Code",
                                "Carton_Type_ID",
                                "MUID",
                                "MDateTime",
                                "Remarks",
                                "OrderStatus",
                                "IsActive",
                                "FinalBy",
                                "EnqNo",
                                "DocNotion",
                                "EstNotion",
                                "FinalDate",
                                "RepID",
                                "ImpExpStatus",
                                "RevQuoteNo",
                                "GrainStyle",
                                "LocationID",
                                "CurrencyID",
                                "Currency_Factctor",
                                "Currency_CurrAmt",
                                "ClientCategoryID",
                                "CalculatedRate",
                                "QuoteRate",
                                "FinalRate",
                                "FPID"
                            ]
                        ),
                        'est_qty': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "quantity": openapi.Schema(type=openapi.TYPE_STRING)
                                },
                                required=["quantity"]
                            )
                        ),
                        'est_board': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "BoardID": openapi.Schema(type=openapi.TYPE_STRING),
                                "Board_Type": openapi.Schema(type=openapi.TYPE_STRING),
                                "Board_GSM": openapi.Schema(type=openapi.TYPE_INTEGER)
                            },
                            required=["BoardID", "Board_Type", "Board_GSM"]
                        ),
                        'est_metpetp': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "MP_FT": openapi.Schema(type=openapi.TYPE_STRING)
                            },
                            required=["MP_FT"]
                        ),
                        'est_print': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "Pr_Complex": openapi.Schema(type=openapi.TYPE_STRING),
                                "Pr_FCol": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "Pr_FB": openapi.Schema(type=openapi.TYPE_STRING),
                                "Pr_Add_Pl": openapi.Schema(type=openapi.TYPE_INTEGER)
                            },
                            required=["Pr_Complex", "Pr_FCol", "Pr_FB", "Pr_Add_Pl"]
                        ),
                        'est_coating': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "FC_Type": openapi.Schema(type=openapi.TYPE_STRING),
                                "FC_Kind": openapi.Schema(type=openapi.TYPE_STRING),
                                "FC_Area": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "FB": openapi.Schema(type=openapi.TYPE_STRING)
                            },
                            required=["FC_Type", "FC_Kind", "FC_Area", "FB"]
                        ),
                        'est_lamination': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "FL_Film": openapi.Schema(type=openapi.TYPE_STRING),
                                "FL_Type": openapi.Schema(type=openapi.TYPE_STRING),
                                "FL_Strips": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "FB": openapi.Schema(type=openapi.TYPE_STRING)
                            },
                            required=["FL_Film", "FL_Type", "FL_Strips", "FB"]
                        ),
                        'est_foiling': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "FF_Film": openapi.Schema(type=openapi.TYPE_STRING),
                                "FF_L": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "FF_B": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "FB": openapi.Schema(type=openapi.TYPE_STRING)
                            },
                            required=["FF_Film", "FF_L", "FF_B", "FB"]
                        )
                    },
                    required=['est_new_quote', 'est_qty', 'est_board', 'est_metpetp', 'est_print', 'est_coating', 'est_lamination', 'est_foiling']
                )
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
            data = request.data
            quote_id = insert_into_est_new_quote(request)
            _ = insert_into_est_qty(request,quote_id)
            if quote_id:
                payload = request.data.get("json_response", {})
                for table_name, table_data in payload.items():
                    if table_name not in ['est_qty', 'est_new_quote']:
                        table_data['QuoteID'] = quote_id
                        with connection.cursor() as cursor:
                            insert_data_into_table(cursor, table_name, table_data)

            return Response({"message": "Data processed successfully", "data": {"quote_id": quote_id} }, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Failed to fetch/save Process Input View information: {str(e)}"
            return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# change the payload json_response or the parsing method
# add all the tables
# parse all informations with dynamic like which contains foiling and what if someone not use foiling manage that payload optional
# Check the cost sheet