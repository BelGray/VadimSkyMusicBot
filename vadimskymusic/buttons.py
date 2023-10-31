from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PlayAboutButtonClient = InlineKeyboardMarkup(row_width=2)
play_about = InlineKeyboardButton(text='▶️ Just listen to it!', callback_data="play_about")
PlayAboutButtonClient.insert(play_about)

PlayTrackButtonClient = InlineKeyboardMarkup(row_width=2)
play_button = InlineKeyboardButton(text="▶️ Play", callback_data="play_button")
info_button = InlineKeyboardButton(text="ℹ️ About", callback_data="about_button")
PlayTrackButtonClient.insert(play_button)
PlayTrackButtonClient.insert(info_button)