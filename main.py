import asyncio
import os
import database.db_config as tables
from aiogram.dispatcher import FSMContext
from vadimskymusic.admin import Admin
from vadimskymusic.engines.extra import Extra
from mutagen.mp3 import MP3
from aiogram.dispatcher.filters.state import State, StatesGroup
from vadimskymusic.buttons import *
from vadimskymusic.loader import *
from database.db_config import *
from vadimskymusic.engines.play_timeout import PlayTimeout
from vadimskymusic.bot_commands import set_default_commands, commands_list
from vadimskymusic.logger import log


class FileImg(StatesGroup):
    img = State()


class UploadFile(StatesGroup):
    file = State()


class DeleteFile(StatesGroup):
    name = State()


class Desc(StatesGroup):
    text = State()

class FileName(StatesGroup):
    name = State()

extra = Extra()
timeout = PlayTimeout(120)


async def on_startup(dispatcher):
    log.s('on_startup', 'Successfully connected to: Telegram API')
    await set_default_commands(dispatcher)


@dp.message_handler(commands=['hot'])
async def hot(message: types.Message):
    text = "🎹 🔥 <b>Catch the TOP 3 most listened tracks in this bot!</b> 🔥 🎹"
    await message.answer(text=text, parse_mode='HTML')
    about_query = conn.execute(
        db.select(tables.tracks).order_by(tables.tracks.columns.listened.desc()).limit(3)
    )
    about = (about_query.fetchall())
    if len(about) == 0:
        await bot.send_message(chat_id=message.chat.id, text='😔 There are not tracks by Vadim! Sorry :(')
        return
    for about in about:
        id = about[0]
        name = about[1]
        listened = about[2]
        image = about[5]
        desc = about[6]
        text = f"🎹 ][{id}][ <b>{name}</b>\n🔥 Listened to (times): {listened}\n🎼 Description:\n{desc}"
        await bot.send_photo(chat_id=message.chat.id, photo=open(image, 'rb'),
                             reply_markup=PlayAboutButtonClient, parse_mode='HTML', caption=text)
    else:
        if len(about) < 3:
            await message.answer(text="☁️ Unfortunately, that's all")


@dp.message_handler(commands=['find_by_name'])
async def find_by_name(message: types.Message):
    text = "🎵 Send the track name: "
    await bot.send_message(chat_id=message.chat.id, text=text)
    await FileName.name.set()

@dp.message_handler(state=FileName.name)
async def process_track_file_name(message: types.Message, state: FSMContext):
    await state.finish()
    name = message.text
    about_query = conn.execute(
        db.select(tables.tracks).where(tables.tracks.columns.name.like(f'%{name}%'))
    )
    about = (about_query.fetchall())
    if len(about) == 0:
        await bot.send_message(chat_id=message.chat.id, text='😔 Track not found! Sorry :(')
        return
    about = about[0]
    id = about[0]
    name = about[1]
    listened = about[2]
    image = about[5]
    desc = about[6]

    text = f"🎹 ][{id}][ <b>{name}</b>\n🔥 Listened to (times): {listened}\n🎼 Description:\n{desc}"
    await bot.send_photo(chat_id=message.chat.id, photo=open(image, 'rb'),
                         reply_markup=PlayAboutButtonClient, parse_mode='HTML', caption=text)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = """
☀️ VadimSkyMusic is a composer who composes tracks on the piano. His music plunges you far into the depths of consciousness and guides you through the valley of memories. So, here you can listen to Vadim's Sky Music to feel these feelings :)
    
☁️ Bot commands:
    /start - ℹ️ Bot info
    /hot - 🔥 Tracks that are listened to most often
    /tracks - 💫 See all VSM tracks
    /find_by_name - 🎵 Find track by name
    """
    await message.answer(text)


@dp.message_handler(commands=['upload'])
async def upload(message: types.Message):
    if Admin.is_admin(message.from_user.id):
        text = "📤 Please, send me an MP3 file with your magic music (remember, that the file name will be displayed as the track name):\n\nSend 'del' if you wanna delete some track."
        await bot.send_message(chat_id=message.chat.id, text=text)
        await UploadFile.file.set()
    else:
        await message.answer('❌ Sorry, but this command is only available for composer')


@dp.message_handler(state=DeleteFile.name)
async def process_delete_file(message: types.Message, state: FSMContext):
    await state.finish()
    path = 'music/' + message.text.strip() + '.mp3'
    if os.path.exists(path):
        os.remove(path)
        conn.execute(
            db.delete(tables.tracks).where(tables.tracks.columns.path == path)
        )
        conn.commit()
        await bot.send_message(chat_id=message.chat.id, text='Track has been deleted successfully! :)')
        return
    await bot.send_message(chat_id=message.chat.id, text=f'Track which named "{message.text}" is not found! :(')


@dp.message_handler(state=UploadFile.file, content_types=['text', 'audio', 'voice'])
async def process_upload_file(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text is not None:
        if "del" in message.text:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Which track do you wanna delete? Please, send the name of this (you can copy the name in /tracks):')
            await DeleteFile.name.set()
            return
    try:
        file_id = message.audio.file_id
        file_name = message.audio.file_name
        path = "music/" + file_name
    except:
        return await bot.send_message(chat_id=message.chat.id,
                                      text="Your message doesn't contain an MP3. Call the command again!")
    if file_name.endswith('.mp3'):
        await bot.download_file_by_id(file_id, destination=path)
        conn.execute(tables.tracks.insert().values([
            {
                'name': os.path.splitext(file_name)[0],
                'listened': 0,
                'listened_recently': 0,
                'path': path,
                'image_path': 'images/VSM.jpeg',
                'description': '\n  ---'
            }
        ]))
        conn.commit()
        await bot.send_message(chat_id=message.chat.id, text='Success! Now your track is available for bot users! :)')
        await bot.send_message(chat_id=message.chat.id,
                               text='🎇 Send a picture of your track.\n\n(Send some text to pass this step)')
        await extra.put(message.from_user.id, 'path', path)
        await FileImg.img.set()
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text="Your message doesn't contain an MP3. Call the command again!")

@dp.message_handler(state=Desc.text, content_types=['text'])
async def process_desc(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == '0':
        await bot.send_message(chat_id=message.chat.id,
                               text="Great! Use /find_by_name command to find your track and check it out")
        return
    conn.execute(
        db.update(tables.tracks).where(
            tables.tracks.columns.path == str(await extra.get(message.from_user.id, 'path', True))).values(
            description=message.text
    ))
    conn.commit()
    await bot.send_message(chat_id=message.chat.id,
                           text="Great! Use /find_by_name command to find your track and check it out")
@dp.message_handler(state=FileImg.img, content_types=['photo', 'text'])
async def process_file_img(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text is not None:
        await bot.send_message(chat_id=message.chat.id,
                               text="📝 Ok, now this track has a default picture. Choose the description (Send '0' to pass): ")
        await Desc.text.set()
        return
    try:
        file_id = message.photo[0].file_id
        file_path = await bot.get_file(file_id)
    except:
        return await bot.send_message(chat_id=message.chat.id, text="Something went wrong!")
    await bot.download_file(file_path.file_path, destination="images/" + file_path.file_path.split("/")[-1])
    conn.execute(
        db.update(tables.tracks).where(
            tables.tracks.columns.path == str(await extra.get(message.from_user.id, 'path', False))).values(
            image_path="images/" + file_path.file_path.split("/")[-1])
    )
    conn.commit()
    await bot.send_message(chat_id=message.chat.id,
                           text="📝 Success! :) Now you can choose the description (Send '0' to pass): ")
    await Desc.text.set()

@dp.message_handler(commands=['tracks'])
async def tracks(message: types.Message):
    # result = conn.execute(db.select([tables.tracks]))
    await message.answer('💫 All available VadimSkyMusic tracks here. Enjoy: ')
    if len(os.listdir('music')) == 0:
        await message.answer(text='O-ops, it seems Vadim hasn\'t posted tracks yet :(')
        return
    for track in os.listdir('music'):
        duration = MP3(f'music/{track}').info.length
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        text = f"🎶 ][ {os.path.splitext(track)[0]} ][\n⏱️ Duration: {'{:02d}:{:02d}'.format(minutes, seconds)} min."
        await message.answer(text, parse_mode='HTML', reply_markup=PlayTrackButtonClient)


@dp.callback_query_handler(text='play_button')
async def play_button_callback(message: types.Message):
    track = (message['message']['text'].split(']['))[1].strip() + '.mp3'
    await bot.send_audio(chat_id=message['message']['chat']['id'], audio=types.InputFile(f'music/{track}'))
    track_name = (message['message']['text'].split(']['))[1].strip()
    if message.from_user.id in timeout.timeout_tracks:
        if track_name in timeout.timeout_tracks[message.from_user.id]:
            return
    conn.execute(
            db.update(tables.tracks).where(tables.tracks.columns.path == f'music/{track}').values(
                listened=tables.tracks.columns.listened + 1, listened_recently=tables.tracks.columns.listened_recently + 1)
    )
    conn.commit()
    await timeout.timeout_user(message.from_user.id, track_name)

@dp.callback_query_handler(text='about_button')
async def about_button_callback(message: types.Message):
    track = (message['message']['text'].split(']['))[1].strip() + '.mp3'
    path = f'music/{track}'
    name = (message['message']['text'].split(']['))[1].strip()
    about_query = conn.execute(
        db.select(tables.tracks).where(tables.tracks.columns.name == f'{name}')
    )
    about = (about_query.fetchall())[0]
    id = about[0]
    listened = about[2]
    image = about[5]
    desc = about[6]

    text = f"🎹 ][{id}][ <b>{name}</b>\n🔥 Listened to (times): {listened}\n🎼 Description:\n{desc}"
    await bot.send_photo(chat_id=message['message']['chat']['id'], photo=open(image, 'rb'), reply_markup=PlayAboutButtonClient, parse_mode='HTML', caption=text)

@dp.callback_query_handler(text='play_about')
async def play_about_button_callback(message: types.Message):
    processing_msg = await bot.send_message(chat_id=message['message']['chat']['id'], text='⌛ Processing...')
    track_id = (message['message']['caption'].split(']['))[1].strip()
    track_name = conn.execute(
        db.select(tables.tracks.columns.name).where(tables.tracks.columns.id == int(track_id))
    ).fetchone()[0]
    track = track_name + '.mp3'
    await bot.send_audio(chat_id=message['message']['chat']['id'], audio=types.InputFile(f'music/{track}'))
    await processing_msg.delete()
    if message.from_user.id in timeout.timeout_tracks:
        if track_name in timeout.timeout_tracks[message.from_user.id]:
            return
    conn.execute(
        db.update(tables.tracks).where(tables.tracks.columns.id == int(track_id)).values(
            listened=tables.tracks.columns.listened + 1, listened_recently=tables.tracks.columns.listened_recently + 1)
    )
    conn.commit()
    await timeout.timeout_user(message.from_user.id, track_name)

@dp.message_handler(content_types=types.ContentType.ANY)
async def on_message(message: types.Message):
    log.i('on_message', f'Message by {message.from_user.full_name} (id: {message.from_user.id}): {message.text}')


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, on_startup=on_startup)
