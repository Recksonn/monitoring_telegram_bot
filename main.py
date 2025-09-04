import telebot
from telebot import types
import db_settings
import os

bot_token = str(open("token.txt", "r", encoding='utf-8').read())
bot = telebot.TeleBot(bot_token)

user_state = {}
current_bot_name = ""
save_markup = ""

buttons_remove = types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Приветствую, {message.from_user.first_name}")

    try:
        if db_settings.is_admin(message.chat.id) == 1:
            config_info = f"""
            Текущий конфиг:
            \nКол-во ботов: {db_settings.count()}
            """
            bot.send_message(message.chat.id, config_info)

        else:
            if str(message.chat.id) == f"{open("owner_id.txt", "r").read()}":
                db_settings.start(message.chat.id)
            else:
                bot.send_message(message.chat.id, "У вас нет доступа к функциям этого бота")

    except Exception:
        if str(message.chat.id) == f"{open("owner_id.txt", "r").read()}":
            db_settings.start(message.chat.id)
        else:
            bot.send_message(message.chat.id, "У вас нет доступа к функциям этого бота")

@bot.message_handler(commands=['settings'])
def settings(message):
    if db_settings.is_admin(message.chat.id) == 1:

        try:
            bot.delete_message(message.chat.id, message_id=(message.id - 1))
            bot.delete_message(message.chat.id, message_id=(message.id - 2))
            bot.delete_message(message.chat.id, message_id=(message.id - 3))
        except Exception:
            pass

        markup = types.InlineKeyboardMarkup(row_width=1)

        button1 = types.InlineKeyboardButton("Управление ботами", callback_data="bots_menu")
        button2 = types.InlineKeyboardButton("Добавить бота", callback_data="add_bot")
        button3 = types.InlineKeyboardButton("Изменить конфиг", callback_data="edit_config")

        markup.add(button1, button2, button3)
        bot.send_message(message.chat.id, "Меню", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к функциям этого бота")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'waiting_for_name')
def create_bot(message):
    bot_name = message.text.strip()
    if bot_name:
        try:
            db_settings.create_table(bot_name)
            bot.send_message(message.chat.id,
                             "Бот создан\nКоманды для бота можно добавить в разделе 'Управление ботами'",
                             reply_markup=buttons_remove)
        except Exception:
            bot.send_message(message.chat.id,
                             "Не удалось создать бота",
                             reply_markup=buttons_remove)
        finally:
            del user_state[message.chat.id]


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'waiting_for_admin')
def create_admin(message):
    admin_id = message.text.strip()
    if admin_id:
        try:
            db_settings.add_admin(admin_id)

            bot.send_message(message.chat.id,
                             f"Администратор добавлен!")
        except Exception:
            bot.send_message(message.chat.id,
                             f"Не удалось добавить администратора!")
        finally:
            del user_state[message.chat.id]


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'waiting_for_new_command')
def add_new_command(message):
    command = message.text.strip()
    if command:
        try:
            db_settings.add_command(current_bot_name, command.split("\n"))
            bot.send_message(message.chat.id, f"Команды успешно добавлены!")
            try:
                bot.delete_message(message.chat.id, message_id=(message.id-1))
                bot.delete_message(message.chat.id, message_id=(message.id-2))
            except Exception:
                pass
        except Exception as ex:
            bot.send_message(message.chat.id, f"Не удалось добавить команды!\n{ex}")
        finally:
            del user_state[message.chat.id]


@bot.message_handler(content_types=['text'])
def text_message(message):
    if db_settings.is_admin(message.chat.id) == 1:
        pass
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к функциям этого бота")
        pass


@bot.callback_query_handler(func=lambda call: True)
def inline_callback(call):
    global current_bot_name, save_markup
    markup = types.InlineKeyboardMarkup(row_width=1)

    if call.message:
        if call.data:
            if "systemctl" in call.data:
                try:
                    if "systemctl status" in call.data:
                        os.system(f"{call.data} > file.txt")
                        with open("file.txt", encoding='utf-8') as file:
                            for line in file.readlines():
                                if line.strip()[:7] == "Active:":
                                    list_output_words = line.strip().split()
                                    for command, description in db_settings.dict_commands(call.data.strip().split("--->")[0]).items():
                                        button = types.InlineKeyboardButton(f"{description}",
                                                                            callback_data=f"{call.data.split("--->")[0]}--->{command}") #Форматирование и передача call.data (Имя бота)
                                        markup.row(button)
                                    menu_button = types.InlineKeyboardButton(f"Вернуться в меню", callback_data="menu")
                                    markup.row(menu_button)

                                    bot.delete_message(call.message.chat.id, message_id=call.message.id)
                                    bot.send_message(call.message.chat.id, f"Управление '{call.data.split("--->")[0]}'\n\n"
                                                                           f"Состояние: {list_output_words[1]} {list_output_words[2]}\n"
                                                                           f"Запущен: {list_output_words[5]} {list_output_words[6]}\n"
                                                                           f"Прошло времени: {list_output_words[-3]} {list_output_words[-2]} {list_output_words[-1]}",
                                                     reply_markup=markup)
                                    break
                                else:
                                    continue
                    else:
                        os.system(call.data)
                        bot.send_message(call.message.chat.id, f"Выполнена команда '{call.data}'")
                except Exception as ex:
                    bot.send_message(call.message.chat.id, f"Не удалось выполнить команду"
                                                           f"\n{ex}")

            elif call.data[:10] == "delete_bot":
                bot.delete_message(call.message.chat.id, message_id=call.message.id)

                try:
                    db_settings.delete_bot(call.data[11:])
                    bot.send_message(call.message.chat.id, f"Бот успешно удалён!")
                except Exception:
                    bot.send_message(call.message.chat.id, f"Не удалось удалить бота!")

            elif call.data[:11] == "new_command":
                bot.delete_message(call.message.chat.id, message_id=call.message.id)
                bot.send_message(call.message.chat.id, f"Введите новую команду для бота '{call.data[12:]}' в формате\n\n"
                                                       f"command1 - Запуск бота\n"
                                                       f"command2 - Остановка бота\n"
                                                       f"command3 - Перезапуск бота\n"
                                                       f"command4 - Статус бота")
                user_state[call.message.chat.id] = 'waiting_for_new_command'
                current_bot_name = call.data[12:]

            elif call.data == "menu":
                button1 = types.InlineKeyboardButton("Управление ботами", callback_data="bots_menu")
                button2 = types.InlineKeyboardButton("Добавить бота", callback_data="add_bot")
                button3 = types.InlineKeyboardButton("Изменить конфиг", callback_data="edit_config")

                markup.add(button1, button2, button3)

                try:
                    bot.delete_message(call.message.chat.id, message_id=call.message.id)
                except Exception:
                    pass
                bot.send_message(call.message.chat.id, "Меню", reply_markup=markup)

            elif call.data == "bots_menu":
                for bot_name in db_settings.bots_elems():
                    keyboard_button = types.InlineKeyboardButton(f"{bot_name}", callback_data=f"{bot_name}")
                    markup.row(keyboard_button)

                menu_button = types.InlineKeyboardButton(f"Вернуться в меню", callback_data="menu")
                markup.row(menu_button)

                bot.delete_message(call.message.chat.id, message_id=call.message.id)
                bot.send_message(call.message.chat.id, "Выберите бота:", reply_markup=markup)

            elif call.data == "add_bot":
                bot.delete_message(call.message.chat.id, message_id=call.message.id)
                bot.send_message(call.message.chat.id, "Введите имя бота:", reply_markup=buttons_remove)
                user_state[call.message.chat.id] = 'waiting_for_name'

            elif call.data == "edit_config":

                button1 = types.InlineKeyboardButton(f"Добавить администратора", callback_data="add_admin")
                button2 = types.InlineKeyboardButton(f"Удалить бота", callback_data="bot_delete")
                button3 = types.InlineKeyboardButton(f"Изменить команды для бота", callback_data="add_command")
                button4 = types.InlineKeyboardButton(f"Вернуться в меню", callback_data="menu")
                markup.add(button1, button2, button3, button4)

                bot.delete_message(call.message.chat.id, message_id=call.message.id)
                bot.send_message(call.message.chat.id, f"Изменить конфиг", reply_markup=markup)

            elif call.data == "add_admin":
                bot.delete_message(call.message.chat.id, message_id=call.message.id)
                bot.send_message(call.message.chat.id,
                                 "Введите chat_id пользователя, которому необходимо дать права администратора")
                user_state[call.message.chat.id] = 'waiting_for_admin'

            elif call.data == "bot_delete":
                bot.delete_message(call.message.chat.id, message_id=call.message.id)

                for bot_name in db_settings.bots_elems():
                    keyboard_button = types.InlineKeyboardButton(f"{bot_name}", callback_data=f"delete_bot {bot_name}")
                    markup.row(keyboard_button)

                bot.send_message(call.message.chat.id, f"Выберите бота для удаления", reply_markup=markup)

            elif call.data == "add_command":
                bot.delete_message(call.message.chat.id, message_id=call.message.id)

                for bot_name in db_settings.bots_elems():
                    keyboard_button = types.InlineKeyboardButton(f"{bot_name}", callback_data=f"new_command {bot_name}")
                    markup.row(keyboard_button)

                bot.send_message(call.message.chat.id, f"Выберите бота для добавления команды", reply_markup=markup)

            else:
                for command, description in db_settings.dict_commands(call.data).items():
                    button = types.InlineKeyboardButton(f"{description}", callback_data=f"{call.data}--->{command}") #Передача имени бота в call.data
                    markup.row(button)
                menu_button = types.InlineKeyboardButton(f"Вернуться в меню", callback_data="menu")
                markup.row(menu_button)

                bot.delete_message(call.message.chat.id, message_id=call.message.id)
                bot.send_message(call.message.chat.id, f"Управление '{call.data.split("--->")[0]}'", reply_markup=markup)


if __name__ == "__main__":
    bot.polling(non_stop=True)
