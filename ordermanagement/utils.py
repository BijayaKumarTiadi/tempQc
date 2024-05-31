from django.db import connections
from django.db import connection
from typing import Optional
import json
from django.http import JsonResponse
from django.db import connection


class DataManager:
    @staticmethod
    def get_itemcodes(response: dict) -> list:
        """
        Extracts item codes from a dictionary response.

        Args:
            response (dict): A dictionary containing response data.

        Returns:
            list: A list of item codes extracted from the response.
        """
        try:
            items = response.get('items', [])
            item_list = [item['item_code'] for item in items]
            return item_list
        except (KeyError, TypeError) as e:
            raise ValueError("Invalid response format") from e

    @staticmethod
    def validate_itemcode(item_codes: list) -> dict:
        """
        Validates a list of item codes and returns product IDs.

        Args:
            item_codes (list): A list of item codes to validate.

        Returns:
            dict: A dictionary mapping item codes to product IDs.
        """
        try:
            with connections['default'].cursor() as cursor:
                product_ids = {}
                for item_code in item_codes:
                    cursor.execute("SELECT ProductID FROM item_fpmasterext WHERE IPREFIX = %s AND isactive = 1", [item_code])
                    result = cursor.fetchone()
                    if result:
                        product_ids[item_code] = result[0]
                    else:
                        product_ids[item_code] = None

            return product_ids

        except Exception as e:
            raise RuntimeError("Database query failed on Validating Item Code :"  + str(e))  
    @staticmethod
    def get_companydata() -> dict:
        """
        Retrieves company data from the database.

        Returns:
            dict: A dictionary mapping company names to their IDs.
        """
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT companyid, companyname FROM companymaster WHERE isactive = 1 ORDER BY companyname")
                companies = cursor.fetchall()
                company_data = {}
                for company_id, company_name in companies:
                    company_data[company_name] = company_id
                return company_data
        except Exception as e:
            raise RuntimeError("Database query failed on Getting Company Data : " + str(e))

    @staticmethod
    def insert_to_temp_table(parsed_data, userid='00002', icompanyid=None, clientid=None, company_address_id=None):
        """
        Insert parsed data into the temporary table and process it.

        Args:
            parsed_data (dict): The parsed data to insert.
            userid (str): The user ID (default: '00002').
            icompanyid (str): The company ID.
            clientid (str): The client ID.
            company_address_id (str): The company address ID.

        Returns:
            str: JSON-formatted response containing the status and inserted data.

        Raises:
            RuntimeError: If database insertion or procedure call fails.
        """
        if not all([icompanyid, clientid, company_address_id]):
            raise ValueError("icompanyid, clientid, and company_address_id must be provided")

        try:
            with connection.cursor() as cursor:
                # Retrieve series ID based on the company ID
                seriseid = get_seriesdata(icompanyid)

                # Call stored procedure to create temp data
                cursor.callproc('Sa_auto_create_temp')

                pono = parsed_data.get('po_number', '')
                customer_name = parsed_data.get('CUSTOMERNAME', '')

                insert_query = """
                    INSERT INTO auto_wo_create (
                        PONO, Itemid, itemname, Quantity, Rate, ItemCode, clientid, CUSTOMERNAME, icompanyid, seriseid, userid, OrderExists, woid, jobno, Batchno, BatchQty, BatchDate, BatchRemarks, company_address_id, Req_DelDate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                items = parsed_data.get('items', [])
                for item in items:
                    item_data = (
                        pono,
                        item.get('productID', ''),
                        item.get('description', ''),
                        item.get('quantity', 0),
                        item.get('unit_price', 0.00),
                        item.get('item_code', ''),
                        clientid,
                        customer_name,
                        icompanyid,
                        seriseid,
                        userid,
                        0,  # OrderExists
                        seriseid,  # woid
                        '',  # jobno
                        '',  # Batchno
                        0,  # BatchQty
                        '',  # BatchDate
                        '',  # BatchRemarks
                        company_address_id,
                        item.get('DEL_DATE', '2060-01-01')
                    )

                    # Execute insertion query
                    cursor.execute(insert_query, item_data)

                # Call stored procedure to create work orders from Excel
                cursor.callproc('WO_Create_From_Excel', [seriseid, userid, icompanyid, "@msg"])

                # Fetch the procedure output message
                cursor.execute("SELECT @msg")
                pstatus = cursor.fetchone()[0]

                # Verify the inserted data
                cursor.execute("SELECT * FROM auto_wo_create WHERE PONO = %s", [pono])
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in rows]

                response = {
                    "status": pstatus,
                    "data": result
                }

                return json.dumps(response)

        except Exception as e:
            raise RuntimeError(f"Database insertion failed: {str(e)}")
        
def get_seriesdata(icompanyid):
    """
    View to retrieve series data for a given company ID.
    
    Args:
        request (HttpRequest): The request object.
        icompanyid (str): The company ID.
    
    Returns:
        JsonResponse: A JSON response containing the series data.
    """
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT MAX(ID)
            FROM seriesmaster 
            WHERE doctype = 'work order' AND isactive = 1 AND ICompanyID = %s;
            """
            cursor.execute(query, [icompanyid])
            series_data = cursor.fetchone()


            return series_data[0]

    except Exception as e:
        return JsonResponse({"error on get series data ": str(e)}, status=500)