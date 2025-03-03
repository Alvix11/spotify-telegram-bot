import os
from config import MAX_SIZE, TELEGRAM_CHANNEL_ID, LOGGER
from database import get_from_db, save_to_db
from spotify import get_info_song, obtener_info_album
from downloader import descargar_musica
from parse_url import limpiar_url
from spotify_track_utils import match_track_with_file

from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

async def start(update: Update, context: CallbackContext) -> None:
    """Handler for the /start command."""
    await update.message.reply_text("🎵 ¡Hola! Envíame un enlace de Spotify para descargar tus canciones preferidas.")

async def manejar_errores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for errors."""
    LOGGER.critical(f"Error: {context.error}")
    await update.message.reply_text("Ocurrió un error inesperado. Por favor, inténtalo de nuevo.")

async def manejar_enlace(update: Update, context: CallbackContext) -> None:
    """Processes the links sent by the user."""
    if not update.message or not update.message.text:
        LOGGER.error("Update no contiene mensaje de texto: %s", update)
        return
    
    url = update.message.text

    if not url.startswith("https://") or "spotify" not in url:
        await update.message.reply_text('❌ Por favor envíame un enlance correcto de "Spotify".')
        LOGGER.warning("'%s' No es un enlace.", url)
        return
    else:
        url_clean = limpiar_url(url)
        data = get_from_db(url_clean)

    if data:
        # If the information is already in the database, reuse the cache.
        file_ids, nombre, artista, album, fecha, imagen_url = data
        file_ids = file_ids.split(",")

        mensaje_info = (
            f"🎧 Track: {nombre}\n"
            f"👤 Artist: {artista}\n"
            f"💽 Album: {album}\n"
            f"📅 Date: {fecha}"
        )
        await update.message.reply_photo(photo=imagen_url, caption=mensaje_info)
        for file_id in file_ids:
            await context.bot.send_audio(chat_id=update.message.chat_id, audio=file_id)
        return

    # Processing playlists is not allowed
    if "/playlist/" in url_clean:
        await update.message.reply_text("❌ No puedo descargar playlists. Solo se permiten álbumes o canciones.")
        return

    # Processing album
    if "/album/" in url_clean:
        album_info = obtener_info_album(url_clean)
        if album_info:
            nombre_album, artista, fecha, imagen_url, canciones = album_info
            mensaje_info = (
                f"💽 Album: {nombre_album}\n"
                f"👤 Artist: {artista}\n"
                f"📅 Date: {fecha}\n"
                f"🎶 Número de canciones: {len(canciones)}"
            )
            await update.message.reply_photo(photo=imagen_url, caption=mensaje_info)
            await update.message.reply_text("🔄 Descargando... esto podría tardar, debido a que es un enlace nuevo en nuestra base de datos, por favor espera unos segundos.")
            
            archivos = descargar_musica(url_clean)
            if not archivos:
                await update.message.reply_text("❌ No se pudo descargar la música.")
                return

            file_ids = []
            
            for archivo in archivos:
                if os.path.getsize(archivo) > MAX_SIZE:
                    os.remove(archivo)
                    await update.message.reply_text(f"❌ {archivo} es demasiado grande (+50MB). No puedo enviarlo.")
                    continue
                
                with open(archivo, "rb") as audio:
                    mensaje = await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio)
                    file_id = mensaje.audio.file_id
                    file_ids.append(file_id)
                    await context.bot.send_audio(chat_id=TELEGRAM_CHANNEL_ID, audio=file_id)
                    
                    url_track = match_track_with_file(archivo, url_clean)
                    if url_track:
                        info_cancion = get_info_song(url_track)
                        if info_cancion:
                            nombre, artistas, album, fecha, imagen_url = info_cancion
                            save_to_db(url_track, [file_id], nombre, artistas, album, fecha, imagen_url)
                os.remove(archivo)
                
            save_to_db(url_clean, file_ids, nombre_album, artista, nombre_album, fecha, imagen_url)
            
        else:
            await update.message.reply_text("❌ No se pudo obtener la información del álbum.")
    else:
        
        # Processing individual track
        await update.message.reply_text("🔄 Descargando tema... Solo espera un poco.")
        archivos = descargar_musica(url_clean)
        if not archivos:
            await update.message.reply_text("❌ No se pudo descargar la música.")
            return

        info_cancion = get_info_song(url_clean)
        if info_cancion:
            nombre, artistas, album, fecha, imagen_url = info_cancion
            mensaje_info = (
                f"🎧 Track: {nombre}\n"
                f"👤 Artist: {artistas}\n"
                f"💽 Album: {album}\n"
                f"📅 Date: {fecha}"
            )
            await update.message.reply_photo(photo=imagen_url, caption=mensaje_info)

            file_ids = []
            for archivo in archivos:
                if os.path.getsize(archivo) > MAX_SIZE:
                    os.remove(archivo)
                    await update.message.reply_text(f"❌ {archivo} es demasiado grande (+50MB). No puedo enviarlo.")
                    continue

                with open(archivo, "rb") as audio:
                    mensaje = await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio)
                    file_ids.append(mensaje.audio.file_id)
                    await context.bot.send_audio(chat_id=TELEGRAM_CHANNEL_ID, audio=mensaje.audio.file_id)
                os.remove(archivo)
            
                save_to_db(url_clean, file_ids, nombre, artistas, album, fecha, imagen_url)
        else:
            await update.message.reply_text("❌ No se pudo obtener la información de la canción.")