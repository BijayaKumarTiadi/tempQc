from django.db import connection
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework import status
from django.http import JsonResponse
from datetime import datetime
def process_dropdown_data(serializer, query, *params):
    cursor = connection.cursor()
    cursor.execute(query, params)
    dropdown_data = cursor.fetchall()
    dropdown_list = [{"label": row[1], "value": row[0]} for row in dropdown_data]
    cursor.close()
    serialized_data = serializer.data
    serialized_data['dropdown_list'] = dropdown_list
    return serialized_data


def insert_into_est_new_quote(request):
    """
    Insert data into the Est_New_quote table.

    This function inserts data into the Est_New_quote table based on the provided request data.

    :param request: The HTTP request object containing the data to be inserted.
    :type request: HttpRequest

    :return: The ID of the newly inserted record.
    :rtype: int or None
    """
    try:
        data = request.data.get("json_response", {}).get("est_new_quote", {})
        """print(data)
        {'QuoteDate': '20231108', 'Quote_No': '123456', 'ICompanyID': 1, 'ClientID': 1001, 'Client_Name': 'Test Client', 'Product_Name': 'Test Product', 'Product_Code': 'PROD-001', 'Carton_Type_ID': 123, 'AUID': 1, 'ADateTime': '2023-11-08T08:00:00', 'MUID': 1, 'MDateTime': '2023-11-08T08:00:00', 'Remarks': 'Test remarks', 'OrderStatus': 'Pending', 'IsActive': True, 'FinalBy': 'John Doe', 'EnqNo': 'ENQ-001', 'DocNotion': 'Doc Notion', 'EstNotion': 'Est Notion', 'FinalDate': '2023-11-10', 'RepID': 123, 'ImpExpStatus': 'Import', 'RevQuoteNo': 'REV-001', 'GrainStyle': 'Grain Style', 'LocationID': 456, 'CurrencyID': 1, 'Currency_Factctor': 1.2, 'Currency_CurrAmt': 1000, 'ClientCategoryID': 789, 'CalculatedRate': 1200.5, 'QuoteRate': 1100.75, 'FinalRate': 1250.25, 'FPID': 456}
        "est_new_quote": {
        "QuoteDate": "2023-11-08",
            "Quote_No": "123456",
            "ICompanyID": "00001",
            "ClientID": "1001",
            "Client_Name": "Test Client",
            "Product_Name": "Test Product",
            "Product_Code": "PROD-001",
            "Carton_Type_ID": 123,
            "AUID": "A123",
            "ADateTime": "2060-01-01 01:01:01",
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
        """
        auid = get_userid(request)
        quote_date = datetime.now().strftime('%Y-%m-%d')[:10]
        ADateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with connection.cursor() as cursor:
            # Construct the SQL query dynamically
            sql = f"""
                INSERT INTO Est_New_quote 
                (QuoteDate, Quote_No, ICompanyID, ClientID, Client_Name, Product_Name, 
                Product_Code, Carton_Type_ID, AUID, ADateTime, MUID, MDateTime, Remarks, 
                OrderStatus, IsActive, FinalBy, EnqNo, DocNotion, EstNotion, FinalDate, 
                RepID, ImpExpStatus, RevQuoteNo, GrainStyle, LocationID, CurrencyID, 
                Currency_Factctor, Currency_CurrAmt, ClientCategoryID, CalculatedRate, 
                QuoteRate, FinalRate, FPID)
                VALUES 
                ('{quote_date}', '{data.get("Quote_No")}', '{data.get("ICompanyID")}', '{data.get("ClientID")}', 
                '{data.get("Client_Name")}', '{data.get("Product_Name")}', '{data.get("Product_Code")}', {data.get("Carton_Type_ID")}, 
                '{auid}', '{ADateTime}', '{data.get("MUID")}', '{data.get("MDateTime")}', '{data.get("Remarks")}', 
                '{data.get("OrderStatus")}', {data.get("IsActive")}, '{data.get("FinalBy")}', '{data.get("EnqNo")}', {data.get("DocNotion")}, 
                '{data.get("EstNotion")}', '{data.get("FinalDate")}', '{data.get("RepID")}', '{data.get("ImpExpStatus")}', {data.get("RevQuoteNo")}, 
                {data.get("GrainStyle")}, '{data.get("LocationID")}', '{data.get("CurrencyID")}', {data.get("Currency_Factctor")}, 
                {data.get("Currency_CurrAmt")}, '{data.get("ClientCategoryID")}', {data.get("CalculatedRate")}, {data.get("QuoteRate")}, 
                {data.get("FinalRate")}, '{data.get("FPID")}')
            """
            cursor.execute(sql)
            quote_id = cursor.lastrowid
            return quote_id
    except Exception as e:
        error_message = f"Failed to insert data into Est_New_quote table: {str(e)}"
        print(error_message)
        return None

def insert_into_est_qty(request, quote_id):
        """
        Insert data into the Est_Qty table.

        This function inserts data into the Est_Qty table based on the provided request data and quote_id.

        :param request: The HTTP request object containing the data to be inserted.
        :type request: HttpRequest
        :param quote_id: The ID of the quote to associate the quantities with.
        :type quote_id: int

        :return: None
        """
        quantities = request.data.get("json_response", {}).get("est_qty", {})
        try:
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



def insert_data_into_table(cursor, table_name, data):
    """
    Insert data into the specified table.

    :param cursor: The cursor object to execute the SQL query.
    :type cursor: Cursor
    :param table_name: The name of the table to insert data into.
    :type table_name: str
    :param data: The data to be inserted into the table.
    :type data: dict
    """
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
        """
        cursor.execute(sql, tuple(data.values()))

        # Commit the transaction
        connection.commit()
        record_id = cursor.lastrowid  # Get the ID of the newly inserted record
        print(f"Data inserted into {table_name} successfully.")
        return record_id 

    except Exception as e:
        error_message = f"Failed to insert data into {table_name} table: {str(e)}"
        print(error_message)
        return None



