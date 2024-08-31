import time
import threading

# Create a bot class
class Bot:
    def __init__(self, bot_id):
        self.bot_id = bot_id
        self.bot_status = 'IDLE'
        self.order_id = None

# Create an order class
class Order:
    def __init__(self, order_id, order_type):
        self.order_id = order_id
        self.order_status = 'PENDING'
        self.order_type = order_type
        self.bot_id = None

# Display all info
def display():
    global pending_vip_orders, pending_normal_orders, complete_orders, bots

    # Headers
    print("")
    print("-" * 31, "MCD", "-" * 31)
    print(f"{'Pending':<21} {'Complete':<15} Bots")
    print("-" * 67)

    # Find maximum rows needed
    orders = pending_vip_orders + pending_normal_orders
    max_rows = max(len(orders), len(complete_orders), len(bots))

    # Iterate through all orders and bots, and display the info in columns
    for i in range(max_rows):
        pending_str = ""
        completed_order_str = ""
        bot_str = ""

        if i < len(orders):
            order = orders[i]
            pending_str = f"{str(order.order_id).zfill(3)}  {order.order_type:<6}  {'Bot'+str(order.bot_id).zfill(3) if order.bot_id else ''}"

        if i < len(complete_orders):
            complete_order = complete_orders[i]
            completed_order_str = f"{str(complete_order.order_id).zfill(3)}"
        
        if i < len(bots):
            bot = bots[i]
            bot_str = f"Bot{str(bot.bot_id).zfill(3)}  {bot.bot_status}"

        print(f"{pending_str:<21} {completed_order_str:<15} {bot_str}")
    return

# Assign an idle bot to a pending order
def assign_bot_to_order():
    global pending_vip_orders, pending_normal_orders, bots

    # Look for an order without a bot
    for order in pending_vip_orders + pending_normal_orders:
        if order.bot_id == None:
            # Look for an IDLE bot
            for bot in bots:
                if bot.bot_status == 'IDLE':
                    if order.order_status == 'PENDING':
                        # Assigned the IDLE bot to an order without a bot
                        bot.bot_status = 'PROCESSING'
                        bot.order_id = order.order_id
                        order.bot_id = bot.bot_id
                        # Create a thread for the 10s timer
                        thread = threading.Thread(target=timer, args=(order,bot,), name="Thread_Order"+str(order.order_id))
                        thread.daemon = True
                        thread.start()
                        break
                    break 

# 10s timer
def timer(order, bot):
    global pending_vip_orders, pending_normal_orders, complete_orders
    t = 10
    while t != 0:
        # Check if the bot is destroyed every second. If so, stop the thread to stop processing the order
        global destroyed
        if [order.order_id, bot.bot_id] in destroyed:
            return
        time.sleep(1)
        t -= 1

    # Remove COMPLETED order from PENDING list
    if order.order_type == 'VIP':
        pending_vip_orders.remove(order)
    else:
        pending_normal_orders.remove(order)
    # Append COMPLETED order into COMPLETE list
    complete_orders.append(order)
    # Change bot status to IDLE
    bot.bot_status = 'IDLE'
    bot.order_id = None

    # Check for suitable assignment again and display updated info
    assign_bot_to_order()
    display()
    print("\nPress 'Enter' to key in command")
    return

# Destroy latest bot
def destroy_latest_bot():
    global pending_vip_orders, pending_normal_orders, complete_orders, bots, destroyed

    # Check if there's any bot left
    if len(bots) == 0:
        print("\nNo bots left to destroy.")
        return

    # Remove latest bot
    destroyed_bot = bots.pop()
    # Check if bot is processing an order
    if destroyed_bot.order_id:
        # Append this bot and its order to the 'destroyed' list to stop the processing thread
        destroyed.append([destroyed_bot.order_id, destroyed_bot.bot_id])
        # Find the assigned order, unassign it, and update new stats
        for order in pending_vip_orders+pending_normal_orders:
            if order.order_id == destroyed_bot.order_id:
                order.bot_id = None
                order.order_status = 'PENDING'
                # Check for suitable assignment again
                assign_bot_to_order() 
                break

x = ""
order_id = 1
bot_id = 1
pending_vip_orders = []
pending_normal_orders = []
complete_orders = []
bots = []
destroyed = [[]]

while True:
    # If the order or bot numbering reaches 999, reset to 1
    if order_id >= 999:
        order_id = 1
    if bot_id >= 999:
        bot_id = 1

    # Display all info
    display()

    # Directory and input
    print("\nA: New VIP Order")
    print("B: New Normal Order")
    print("C: + Bot")
    print("D: - Bot")
    print("R: Exit")
    print("E: Exit")
    x = input("Enter: ").upper()

    # Input action controller
    if x == 'A':
        order = Order(order_id, 'VIP')
        pending_vip_orders.append(order)
        order_id += 1
        assign_bot_to_order()
    elif x == 'B':
        order = Order(order_id, 'NORMAL')
        pending_normal_orders.append(order)
        order_id += 1
        assign_bot_to_order()
    elif x == 'C':
        bot = Bot(bot_id)
        bots.append(bot)
        bot_id += 1
        assign_bot_to_order()
    elif x == 'D':
        destroy_latest_bot()
    elif x == "R" or x == "":
        continue
    elif x == 'E':
        print("\nTerminate program")
        break
    else:
        print("\nInvalid input")