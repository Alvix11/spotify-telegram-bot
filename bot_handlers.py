import os
from config import MAX_SIZE, TELEGRAM_CHANNEL_ID, LOGGER
from database import get_from_db, save_to_db
from spotify import get_info_song, get_info_album
from downloader import music_download
from parse_url import clean_url
from spotify_track_utils import match_track_with_file

from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

async def start(update: Update, context: CallbackContext) -> None:
    """Handler for the /start command."""
    await update.message.reply_text("🎵 ¡Hola! Envíame un enlace de Spotify para descargar tus canciones preferidas.")

async def error_handling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for errors."""
    LOGGER.critical(f"Error: {context.error}")
    await update.message.reply_text("Ocurrió un error inesperado. Por favor, inténtalo de nuevo.")

async def handle_link(update: Update, context: CallbackContext) -> None:
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
        url_clean = clean_url(url)
        data = get_from_db(url_clean)

    if data:
        # If the information is already in the database, reuse the cache.
        file_ids, name, artist, album, date, image_url = data
        file_ids = file_ids.split(",")

        info_message = (
            f"🎧 Track: {name}\n"
            f"👤 Artist: {artist}\n"
            f"💽 Album: {album}\n"
            f"📅 Date: {date}"
        )
        await update.message.reply_photo(photo=image_url, caption=info_message)
        for file_id in file_ids:
            await context.bot.send_audio(chat_id=update.message.chat_id, audio=file_id)
        return

    # Processing playlists is not allowed
    if "/playlist/" in url_clean:
        await update.message.reply_text("❌ No puedo descargar playlists. Solo se permiten álbumes o canciones.")
        return

    # Processing album
    if "/album/" in url_clean:
        album_info = get_info_album(url_clean)
        if album_info:
            name_album, artist, date, image_url, songs = album_info
            info_message = (
                f"💽 Album: {name_album}\n"
                f"👤 Artist: {artist}\n"
                f"📅 Date: {date}\n"
                f"🎶 Numbers tracks: {len(songs)}"
            )
            await update.message.reply_photo(photo=image_url, caption=info_message)
            await update.message.reply_text("🔄 Descargando... esto podría tardar, debido a que es un enlace nuevo en nuestra base de datos, por favor espera unos segundos.")
            
            files = music_download(url_clean)
            if not files:
                await update.message.reply_text("❌ No se pudo descargar la música.")
                return

            file_ids = []
            
            for file in files:
                if os.path.getsize(file) > MAX_SIZE:
                    os.remove(file)
                    await update.message.reply_text(f"❌ {file} es demasiado grande (+50MB). No puedo enviarlo.")
                    continue
                
                with open(file, "rb") as audio:
                    message = await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio)
                    file_id = message.audio.file_id
                    file_ids.append(file_id)
                    await context.bot.send_audio(chat_id=TELEGRAM_CHANNEL_ID, audio=file_id)
                    
                    url_track = match_track_with_file(file, url_clean)
                    if url_track:
                        info_song = get_info_song(url_track)
                        if info_song:
                            name, artist, album, date, image_url = info_song
                            save_to_db(url_track, [file_id], name, artist, album, date, image_url)
                os.remove(file)
                
            save_to_db(url_clean, file_ids, name_album, artist, name_album, date, image_url)
            
        else:
            await update.message.reply_text("❌ No se pudo obtener la información del álbum.")
    else:
        
        # Processing individual track
        await update.message.reply_text("🔄 Descargando tema... Solo espera un poco.")
        files = music_download(url_clean)
        if not files:
            await update.message.reply_text("❌ No se pudo descargar la música.")
            return

        info_song = get_info_song(url_clean)
        if info_song:
            name, artist, album, date, image_url = info_song
            info_message = (
                f"🎧 Track: {name}\n"
                f"👤 Artist: {artist}\n"
                f"💽 Album: {album}\n"
                f"📅 Date: {date}"
            )
            await update.message.reply_photo(photo=image_url, caption=info_message)

            file_ids = []
            for file in files:
                if os.path.getsize(file) > MAX_SIZE:
                    os.remove(file)
                    await update.message.reply_text(f"❌ {file} es demasiado grande (+50MB). No puedo enviarlo.")
                    continue

                with open(file, "rb") as audio:
                    message = await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio)
                    file_ids.append(message.audio.file_id)
                    await context.bot.send_audio(chat_id=TELEGRAM_CHANNEL_ID, audio=message.audio.file_id)
                os.remove(file)
            
                save_to_db(url_clean, file_ids, name, artist, album, date, image_url)
        else:
            await update.message.reply_text("❌ No se pudo obtener la información de la canción.")