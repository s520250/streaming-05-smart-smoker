"""
Author: Sammie Bever
Date: February 3, 2023 
Class: Streaming Data 
Assignment: Module 05

This program uses producers and task queues (RabbitMQ).
It reads data from the smoker-temps.csv file for smart smokers.

To-Do List:
- file is sending 3 messages to all 3 queues each time... I think it needs some type of 
    routing or if statements to tell it when to send which messages to certain queues
- change sleep time

"""
########################################################

# import python modules
import pika
import sys
import webbrowser
import csv
# import socket
import time

########################################################

# define variables/constants/options
host = "localhost"
# port = 9999
# address_tuple = (host, port)
csv_file = "smoker-temps.csv"
smoker_queue = "01-smoker"
foodA_queue = "02-food-A"
foodB_queue = "03-food-B"
show_offer = True # (RabbitMQ Server option - T=on, F=off)
# socket_family = socket.AF_INET 
# socket_type = socket.SOCK_DGRAM

########################################################

# define functions
## define option to open RabbitMQ admin webpage
def offer_rabbitmq_admin_site(show_offer):
    # includes show_offer variable - option to turn off the offer later in the code
    if show_offer == True:
        """Offer to open the RabbitMQ Admin website"""
        ans = input("Would you like to monitor RabbitMQ queues? y or n ")
        print()
        if ans.lower() == "y":
            webbrowser.open_new("http://localhost:15672/#/queues")
            print()

## define delete_queue
def delete_queue(host: str, queue_name: str):
    """
    Delete queues each time we run the program to clear out old messages.
    """
    conn = pika.BlockingConnection(pika.ConnectionParameters(host))
    ch = conn.channel()
    ch.queue_delete(queue=queue_name)

## define main work of program

### define a message to send to queue
def publish_message_to_queue(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """
    ### Get a connection to RabbitMQ and create a channel
    try:
        # create a connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # declare a durable queue (will survive a RabbitMQ server restart
        # and help ensure messages are processed in order)
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue; each message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        print(f" [x] Sent {message} to {queue_name}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

def get_message_from_csv(input_file):
    """
    Read from csv input file. Send each row as a message to the queue.
    """ 
    # sock = socket.socket(socket_family, socket_type) 

    # read from a csv file
    input_file = open(csv_file, "r")
    reader = csv.reader(input_file, delimiter=',')

    # Skip reading the header row of csv
    next(reader)

    # Write the header row to the output file
    # header_list = ['Time (UTC)', 'Channel1', 'Channel2', 'Channel3']

    for row in reader:
        input_string_row1 = row[1]
        input_string_row2 = row[2]
        input_string_row3 = row[3]

        to_convert_column1 = input_string_row1.replace('', '0')
        to_convert_column2 = input_string_row2.replace('', '0')
        to_convert_column3 = input_string_row3.replace('', '0')

        float_row1 = float(to_convert_column1)
        float_row2 = float(to_convert_column2)
        float_row3 = float(to_convert_column3)

        # get the "timestamp" column 
        fstring_time = f"{row[0]}"
        fstring_channel1 = f"{row[1]}"
        fstring_channel2 = f"{row[2]}"
        fstring_channel3 = f"{row[3]}"

        # convert columns to float types
        # Channel1 = float(row[1])
        # Channel2 = float(row[2])
        # Channel3 = float(row[3])

        # use an fstring to create messages from our data
        fstring_message_smoker = f"[{fstring_time}, {fstring_channel1}]"
        fstring_message_foodA = f"[{fstring_time}, {fstring_channel2}]"
        fstring_message_foodB = f"[{fstring_time}, {fstring_channel3}]"

        # used this code in mod4, but not mod2... not sure if needed
        # input_file.read

        # prepare a binary (1s and 0s) message to stream
        # 'message' is case sensitive!
        message_smoker = fstring_message_smoker.encode()
        message_foodA = fstring_message_foodA.encode()
        message_foodB = fstring_message_foodB.encode()

        # use the socket sendto() method to send the message
        # sock.sendto(message_smoker, address_tuple)
        # sock.sendto(message_foodA, address_tuple)
        # sock.sendto(message_foodB, address_tuple)

        # publish message to queue
        # publish_message_to_queue(host, smoker_queue, message_smoker)
        # publish_message_to_queue(host, foodA_queue, message_foodA)
        # publish_message_to_queue(host, foodB_queue, message_foodB)

        # publish using routing
        if float_row1 > 0: publish_message_to_queue(host, smoker_queue, message_smoker)
        if float_row2 > 0: publish_message_to_queue(host, foodA_queue, message_foodA)
        if float_row3 > 0: publish_message_to_queue(host, foodB_queue, message_foodB)
        else: print()

        # slowly read a row every 1 seconds from file
        time.sleep(1)        

########################################################

# Run program
if __name__ == "__main__":  
    # if show_offer = True, ask the user if they'd like to open the RabbitMQ Admin site
    offer_rabbitmq_admin_site(show_offer)
    # delete queues to clear old messages
    delete_queue(host, smoker_queue)
    delete_queue(host, foodA_queue)
    delete_queue(host, foodB_queue)
    # get the message from the csv input file and send to queue
    get_message_from_csv(csv_file)
