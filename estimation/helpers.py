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


