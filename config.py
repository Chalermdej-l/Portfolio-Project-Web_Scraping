import pyodbc as py

class configscape:
    Driver = 'SQL Server'
    Server_name = '(local)'
    Database_name = 'scape_booking'

    col_name = ['lati','long','type','hotel_name', 'city_name',
       'region_name', 'country_name', 'dest_type','dest_id','hotel_id',
       'currency', 'score_wifi', 'score_paid_wifi', 'score_breakfast',
       'score_staff', 'score_services', 'score_clean', 'score_comfort',
       'score_value', 'score_location', 'score_total', 'score_accuracy',
       'score_pool', 'score_walking', 'url_index','inuse']
    order_col = ['hotel_id','dest_id','hotel_name','inuse','type','dest_type','currency','city_name',
    'region_name','country_name', 'lati','long', 'score_wifi', 'score_paid_wifi', 'score_breakfast',        
        'score_staff', 'score_services', 'score_clean', 'score_comfort',
        'score_value', 'score_location', 'score_accuracy',
        'score_pool', 'score_walking', 'score_total','url_index']

    query = '''
    insert into [scape_booking].[dbo].[Hotel_Info]
    select
    ? [Hotel_Id],
    ?       [Dest_Id],
    ?       [Hotel_name],
    ?       [In_use],
    ?       [Type],
    ?       [Dest_type],
    ?       [Currency],
    ?       [City],
    ?       [Region],
    ?       [Country],
    ?       [Latitude],
    ?       [Longitude],
    ?       [Score_wifi],
    ?       [Score_paidwifi],
    ?       [Score_breakfast],
    ?       [Score_staff],
    ?       [Score_service],
    ?       [Score_clean],
    ?       [Score_comfort],
    ?       [Score_value],
    ?       [Score_location],
    ?       [Score_accuary],
    ?       [Score_pool],
    ?       [Score_walking],
    ?       [Score_final],
    ?       [url_index]
    '''

    inputsize = [
         (py.SQL_INTEGER)
        , (py.SQL_DECIMAL,10,0)
        , (py.SQL_VARCHAR, 500, 0)
         , (py.SQL_INTEGER)
        , (py.SQL_VARCHAR, 100, 0)
        , (py.SQL_VARCHAR, 100, 0)
        , (py.SQL_VARCHAR, 10, 0)
        , (py.SQL_VARCHAR, 100, 0)
        , (py.SQL_VARCHAR, 100, 0)
        , (py.SQL_VARCHAR, 100, 0)
        , (py.SQL_DECIMAL,18,6)
        , (py.SQL_DECIMAL,18,6)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_DECIMAL,3,1)
        , (py.SQL_INTEGER)
    ]