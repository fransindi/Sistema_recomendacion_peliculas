from fastapi import FastAPI
import pandas as pd

#instanciamos la api
app = FastAPI()



#leemos la tabla
data = pd.read_csv('data/peliculas_ETL.csv')
df = data.copy()

# para la funcion 1 y 2, debo aplicar esta modificacion.
#  comentare cada una con respecto a la funcion que corresponden
df['release_date'] = pd.to_datetime(df['release_date'])


#funcion3:
#aplicamos un trim para eliminar espacios
df['title'] = df['title'].str.strip()

#funcion7:
import joblib
df_ml = pd.read_csv('data/df_ml.csv')
similarity_matrix = joblib.load('pickle/similarity_matrix.pkl')


#Damos la bienvenida en nuestro root
@app.get('/')
async def inicio():
    return 'Bienvenidos a esta api de peliculas, comienza la aventura!'



#Funcion 1: Cantidad de films estrenados por mes.
@app.get('/films_mes/{mes}')
async def cantidad_filmacion_mes(mes: str = None):
    """
    Devuelve la cantidad de films estrenados en un mes.

    parametros
    ---------
    mes: un string con el nombre del mes en español, ej: enero
    """
    #evitamos errores con lower()
    mes = mes.lower()
    #creamos una lista con los meses en minuscula
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    #si el mes no se encuentra en la lista devuelve un ejemplo
    if mes not in meses:
        return "ingresa el nombre de un mes en español. Ej: Agosto"
    #si existe tomamos el indice del mes.
    indice_mes = meses.index(mes)
    #de nuestro df recuperamos en orden los valores de las peliculas que se estrenaron en cada mes.
    valores_mes = list(df.release_date.dt.month.value_counts().sort_index())
    return {'mes': mes.title(), 'cantidad': valores_mes[indice_mes]}



#Funcion 2. Cantidad de films estrenados por dia de la semana
@app.get('/films_dia/{dia}')
async def cantidad_filmaciones_dia(dia: str = None):
    """
    Devuelve la cantidad de films estrenados en dias de la semana

    parametros
    -----------
    dia: nombre del dia de la semana en español. ej: lunes
    """
    #minimizamos errores.
    dia = dia.lower()
    #lista con los dias de la semana en minuscula
    semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    #chequeamos si el dia se encuentra en nuestra semana.
    if dia not in semana:
        return "ingresa el nombre del dia en español. ej: Lunes"
    #recuperamos el indice
    indice_semana = semana.index(dia)
    #lista con cantidades de pelicula por dia.
    valores_semana = list(df.release_date.dt.weekday.value_counts().sort_index())
    return {'dia': dia.title(), 'cantidad': valores_semana[indice_semana]}

#Funcion 3. Devolver un titulo con el anio de estreno y el score
@app.get('/score_titulo/{titulo}')
async def score_titulo(titulo: str = None):
    """
    Devuelve titulo, anio de estreno y score de una 
    pelicula de nuestra base de datos.

    parametros
    ----------
    titulo: titulo de la pelicula completo.
    """
    #input a minusculas para evitar errores
    titulo = titulo.lower()
    #hacemos un try except, si pasa se completa la funcion
    try:
        #creamos una mascara para la pelicula
        mask = df[df['title'].str.lower()  == titulo]
        #extraemos valores y damos respuesta.
        anio = mask['release_year'].values[0]
        score = mask['popularity'].values[0]
        dicc = {'titulo': titulo.title(), 'anio': int(anio), 'popularidad': float(score)}
        return dicc
    except:
        #si no pasa se pide otra pelicula
        return 'Ingresa por favor el nombre de la pelicula. ej: Toy Story'
    
    

#Funcion 4. Devolver el titulo, el promedio de votos y la cantidad de votos.
@app.get('/votes_titulo/{titulo}')
async def votes_titulo(titulo: str = None):
    """
    Dado un titulo devolvemos el promedio de votos y la cantidad de votos
    siempre y cuando cuente con mas de 2000 votos.

    parametros
    ----------
    titulo: titulo de la pelicula
    """
    #hacemos un try except para chequear si el titulo existe.
    try:
        #creamos una mascara.
        mask = df[df.title.str.lower() == titulo.lower()]
        #recuperamos la cantidad de votos y el promedio
        cantidad_votos = mask['vote_count'].values[0]
        promedio_votos = mask['vote_average'].values[0]
        anio = mask['release_year'].values[0]
        #si no cumple con 2000 votos o mas
        if cantidad_votos < 2000:
            #la funcion termina
            return f"esta pelicula tiene {cantidad_votos} de votos. Por lo que no pasa la condicion de esta funcion"
        #sino
        else:
            return {'titulo': titulo.title(), 'anio': int(anio), 'cantidad_votos': cantidad_votos, 'promedio_votos': promedio_votos}
    except:
        return "Ingresa el nombre de la pelicula. ej: Toy Story"
    


#funcion 5. Segun un actor dado devuelve la cantidad de peliculas en que actuo, el total de retorno y el promedio
@app.get('/actor/{actor_name}')
async def get_actor(actor_name: str = None):
    """
    Devuelve la cantidad de peliculas, el total de retorno 
    y el promedio de retorno
    
    parametros
    ----------
    actor_name: nombre del actor, tipo str.
    """
    try:
        #iniciamos una lista vacia
        lista_indices_actor = []
        #iteramos por el dataframe
        for i in range(0, df.shape[0]):
            #instanciamos cada fila
            fila = df.iloc[i, -3]
            #si la fila no es nula
            if fila != 'N/D':
                fila = eval(fila)
                #iteramos la lista de actores
                for x in fila:
                    #si el actor se encuentra
                    if x.lower() == actor_name.lower():
                        #lo añadimos a la lista 
                        lista_indices_actor.append(i)
        #traemos una serie con los indices en que se encontraba el actor
        actor_series = df.iloc[lista_indices_actor, -3]
        #creamos un nuevo dataframe con las columnas a utilizar
        df2 = df[['title', 'return']]
        #le agregamos la columna del actor
        df2['actor_buscado'] = actor_series
        #creamos una mascara sin los nulos
        mask = df2[df2['actor_buscado'].notnull()]
        #extraemos valores.
        cantidad_peliculas = mask.shape[0]
        total_return = mask['return'].sum()
        promedio_return = mask['return'].mean()
        return {'actor': actor_name.title(), 'cantidad_filmaciones': cantidad_peliculas, 'retorno_total': total_return, 'retorno_promedio': promedio_return}
    except:
        return {'ingresa el nombre del actor correctamente. ej: Brad Pitt'}
    



#funcion 6: devolver lista de peliculas y exito del director segun el director
@app.get('/director/{director}')
async def get_director(director: str = None):
    """
    Dado un director devuelve una lista con las peliculas, fecha de estreno, 
    budget, revenue, return y el exito del director

    parametros
    ----------
    director: nombre del director. tipo str.
    """
    director = director.lower()
    try:
        #iniciamos una lista de indices vacia
        lista = []
        #iteramos el dataframe
        for i in range(0, df.shape[0]):
            fila = df.iloc[i, -4]
            if type(fila) == str:
                if fila != 'N/D':
                    #si la fila es igual al director:
                    if fila.lower() == director:
                        #agregamos el indice a la lista
                        lista.append(i)
        
        #con la lista creamos una serie con los directores
        directores_serie = df.iloc[lista, -4]
        #creamos un dataframe con las columnas que necesitamos
        df2 = df[['title', 'release_date', 'budget', 'revenue', 'return']].copy()
        #agregamos la columna director
        df2['director'] = directores_serie
        #creamos una mascara sin los nulos
        mask = df2[df2['director'].notnull()]

        #arreglamos el formato de fecha
        mask['release_date'] = mask['release_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        
        retorno = mask['return'].sum()

        anios = list(mask['release_date'].values)[0:5]
        retorno_pelicula = list(mask['return'].values[0:5])
        revenue_pelicula = list(mask['revenue'].values[0:5])
        budget_pelicula = list(mask['budget'].values[0:5])
        dicc_peliculas = {'titulo': list(mask.title.values)[0:5], 'anio': anios, 'retorno_pelicula': retorno_pelicula, 'budget_pelicula': budget_pelicula, 'revenue_pelicula': revenue_pelicula}

        #damos respuesta
        return {'director': director.title(), 'retorno_total': retorno, 'peliculas': dicc_peliculas}
    except:
        return 'Ingresa el nombre del director correctamente. ej: Steven Spielberg.'

            

@app.get('/recomendacion/{titulo}')
async def recomendacion(titulo: str = None):
    try:
        movie_index = df_ml[df_ml['title'] == titulo].index[0]
        similarity_scores = list(enumerate(similarity_matrix[movie_index]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        top_scores = similarity_scores[1:5+1]
        top_movie_indices = [score[0] for score in top_scores]
        top_movies = df_ml['title'].iloc[top_movie_indices]
        dicc = {}
        for i, v in enumerate(top_movies.values):
            dicc[i + 1] = v
        return {'lista_recomendada': dicc}
    except: 
        return 'Ingresa el nombre de la pelicula correctamente, ej: Toy Story.'