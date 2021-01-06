import telebot
import logging
import os
from option_selecting import *
IS_TEST = False
TOKEN = os.environ.get("STOCK_TELEGRAM_TOKEN")


##Setting ---------------------------------
## Load TOKEN
try:
    import API_TOKEN
    TOKEN = API_TOKEN.API_TOKEN
    print(TOKEN)
    IS_TEST = True
except:
    pass

#Set logger
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

#Init the Bot
bot = telebot.TeleBot(TOKEN)
print(f"The Token is {TOKEN}")

#Main Funciton ---------------------------------
# Menu
@bot.message_handler(commands=['start'])
def send_start(message):
    """
    Show Main Menu
    :param message: message
    :return: None
    """
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    #Keyborad Options
    start_markup.row('/start', '/help', '/hide')
    start_markup.row('/option')

    bot.send_message(message.chat.id, "Bot has started")
    bot.send_message(message.from_user.id, "⌨️ The Keyboard is added!\n⌨️ /hide To remove kb ",
                     reply_markup=start_markup)

#Hide Keyboard
@bot.message_handler(commands=["hide"])
def hide_command(message):
    """
    Show Hiding Commands
    :param message: message
    :return: None
    """
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Keyboard Hide", reply_markup=hide_markup)

# Show Help
@bot.message_handler(commands=["help"])
def show_help(message):
    """
    Show Help Commands
    :param message: messag
    :return:
    """
    bot.send_message(message.chat.id, "/start - display the keyboard\n"
                                      "/option - suggest the option\n", ""
                     )

#---------------------------------
#Stock Function Commands

@bot.message_handler(commands=["option"])
def suggest_option_command(message):
    """
    Ask for ticker for option suggestion
    :param message: message
    :return:
    """
    sent = bot.send_message(message.chat.id,"Enter the Ticker")
    bot.register_next_step_handler(sent,get_option_suggestion)

def get_option_suggestion(message):
    """
    Process Option Suggestion
    :param message: messagse
    :return:
    """

    ticker = message.text
    threshold = 0.8
    v_min = 5000000

    try:
        avg, iv = get_avg_volatility(ticker)
        if avg > threshold and get_volume(ticker) > v_min:
            bot.send_message(message.chat.id, "Yes")
        else:
            bot.send_message(message.chat.id, "No")
    except:
        ##Handle Error
        bot.send_message(message.chat.id,"Error Processing. Please Try Again")




#Wild Card---------------------------------
# Unknown Command
@bot.message_handler(func=lambda f: True)
def wrong_command(message):
    """
    Handle Wrong or Unknow Commands
    :param message: message
    :return: None
    """
    bot.send_message(message.chat.id, "Unknown Command")
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    start_markup.row('/start', '/help', '/hide')
    start_markup.row("/option")
    bot.send_message(message.chat.id, "Again", reply_markup=start_markup)

#ACB AMC


#---------------------------------
#main function
#start the bot

if IS_TEST:
    bot.polling()
else:
    while True:
        try:
            bot.polling()
        except:
            bot.polling()