from django.http import JsonResponse
import jwt
import psycopg2


conn = psycopg2.connect(
    dbname="dwr_staging",
    user="root",
    password="password",
    host="localhost",
    port="5432"
)

def middleware(get_response):
    
    def middleware(request):
        
        try:   
            token_Get=request.headers['Authorization'].split("Bearer ")[1]
            secret_key =  'dSUNYPjdhqSqRrowcRuR30uSiHNw'
            
            decoded_token = jwt.decode(token_Get, secret_key, algorithms='HS256')
            print("+-=-=-=-=-=-=-=->",decoded_token)
            # if token_Get:

            #     with conn.cursor() as cursor:
            #         cursor.execute("SELECT * FROM public.user")

            #     rows = cursor.fetchall()
            #     for i in rows:
            #         if i.jwt_token == token_Get and i.id == decoded_token.get('id') and i.role =='HR':
            #             break
            #     else:
            #         return JsonResponse({'status':401,'message':'Unauthenticated user','data':''})
        except Exception as e:
             return JsonResponse({'status':400,'message':str(e), 'data':''})
        response = get_response(request)
        return response

    return middleware