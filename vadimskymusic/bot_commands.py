from aiogram import types

commands_list = ('start', 'hot', 'tracks', 'find_by_name', 'upload')
async def set_default_commands(dp):
    """Команды telegram бота"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "ℹ️ Bot info"),
            types.BotCommand("hot", "🔥 Tracks that are listened to most often"),
            types.BotCommand('tracks', "💫 See all VSM tracks"),
            types.BotCommand("find_by_name", "🎵 Find track by name"),
            #types.BotCommand("profile", "👤 My profile"),
            types.BotCommand("upload", "🆕 Upload new track. This command is only available for Vadim :)")
        ]
    )