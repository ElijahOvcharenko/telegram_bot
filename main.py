"""
для запуска в фоновом режиме: nohup python3 main.py &
для закрытия нужно сначала найти процесс: ps aux|grep main.py, а потом убить: kill <PID_процесса>
"""

from RoomBot import RoomBot

bot = RoomBot()
bot.run()
