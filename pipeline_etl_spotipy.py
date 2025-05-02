
import json
import base64
import requests
import pandas as pd
import spotipy

# Cargar las credenciales de la API desde un archivo JSON
def load_credentials(filename = 'key.json'):
    with open(filename) as archivo:
        credenciales = json.load(archivo)
    return credenciales['CLIENT_ID'], credenciales['CLIENT_SECRET']

# Obtener token de acceso de Spotify
def get_access_token(client_id, client_secret):
    # Codificacion de client id y client secret
    client_credentials = f"{client_id}:{client_secret}"
    client_credentials_base64 = base64.b64encode(client_credentials.encode())
    
    # Solicitud de token de acceso
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {client_credentials_base64.decode()}'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code == 200:
        access_token = response.json()['access_token']
        print("Se ha obtenido el token de acceso con exito")
        return access_token 
    else:
        print("Error al obtener el token de acceso")
        exit()
        
# Extraer datos de las canciones en una playlist
def get_playlist_tracks(playlist_id, access_token):
    # Configuracion de spotipy con el token de acceso
    sp = spotipy.Spotify(auth= access_token)
    # Obtiene las tracks de la playlist
    playlist_traks = sp.playlist_tracks(playlist_id, fields= 'items(track(id, name, artists, album(id, name)))')

    # Extraccion de informacion relevante y almacenamiento en una lista de diccionarios
    music_data = []
    for track_info in playlist_traks['items']:
        track = track_info['track']
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        album_id = track['album']['id']
        track_id = track['id']
        
        # Obtener fecha de lanzamiento del album
        try:
            album_info = sp.album(album_id) if album_id != 'Not available' else None
            release_date = album_info['release_date'] if album_info else None
        except:
            release_date = None

        # Obtener popularidad del track
        try:
            track_info = sp.track(track_id) if track_id != 'Not available' else None
            popularity = track_info['popularity'] if track_info else None
        except:
            popularity = None
        
        # Agregar informacion adicional
        track_data = {
            'Track Name': track_name,
            'Artists': artists,
            'Album Name': album_name,
            'Album ID': album_id,
            'Track ID': track_id,
            'Popularity': popularity,
            'Release Date': release_date,
            'Explicit': track_info.get('explicit', None),
            'External URLs': track_info.get('external_urls', {}).get('spotify', None),
        }

        music_data.append(track_data)
    
    return music_data

# Obtener la fecha de lanzamiento del álbum
def get_album_release_date(sp, album_id):
    try:
        album_info = sp.album(album_id) if album_id != 'Not available' else None
        return album_info['release_date'] if album_info else None
    except Exception as e:
        print(f"Error al obtener fecha de lanzamiento del álbum: {e}")
        return None

# Obtener la popularidad del track
def get_track_popularity(sp, track_id):
    try:
        track_info = sp.track(track_id) if track_id != 'Not available' else None
        return track_info['popularity'] if track_info else None
    except Exception as e:
        print(f"Error al obtener popularidad del track: {e}")
        return None

# Cargar los datos en un DataFrame y guardarlos como archivo CSV
def load_data_to_csv(music_data, filename="musicdata.csv"):
    df = pd.DataFrame(music_data)
    df.to_csv(filename, index=False)
    print(f"Datos guardados en {filename}")
    
# Pipeline ETL completo
def run_etl_pipeline(playlist_id, client_id, client_secret):
    access_token = get_access_token(client_id, client_secret)
    music_data = get_playlist_tracks(playlist_id, access_token)
    load_data_to_csv(music_data)
    
if __name__ == '__main__':
    CLIENT_ID, CLIENT_SECRET = load_credentials()
    playlist_id = '4wWiubixuCDlS5zLeVuPx1'  # ID de la playlist que quieres consultar
    run_etl_pipeline(playlist_id, CLIENT_ID, CLIENT_SECRET)
