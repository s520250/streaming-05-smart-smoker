"""
Author: Sammie Bever
Date: February 3, 2023 
Class: Streaming Data 
Assignment: Module 05

This program uses producers and task queues (RabbitMQ).
It reads data from the smoker-temps.csv file for smart smokers.

Questions to come back to later:
- how to delete a channel?

"""
# import python modules
import pika
import sys
import webbrowser
import csv
import socket
import time

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

## define main work of program

### define a message to send to queue
def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """
    ### Get a connection to RabbitMQ, and a channel, 
    ### delete the 3 existing queues (we'll likely run this multiple times), and then declare them anew
    host = "localhost"
    port = 9999
    address_tuple = (host, port)

    socket_family = socket.AF_INET 
    socket_type = socket.SOCK_DGRAM 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    # read (slowly) from a csv file
    input_file = open("smoker-temps.csv", "r")
    reader = csv.reader(input_file, delimiter=',')
    # Our file has a header row, move to next to get to data
    header = next(reader)

    # Write the header row to the output file
    header_list = [Time(UTC),Channel1,Channel2,Channel3]

    for row in reader:
        # read a row from the file
        Time(UTC), Channel1, Channel2, Channel3 == row

        # use an fstring to create a message from our data
        fstring_message1 = f"[{'Time (UTC)'}, {'Channel1'}]"
        fstring_message2 = f"[{'Time (UTC)'}, {'Channel2'}]"
        fstring_message3 = f"[{'Time (UTC)'}, {'Channel3'}]"

# used this code in mod4, but not mod2... not sure if needed
        # input_file.read

        # prepare a binary (1s and 0s) message to stream
        # 'message' is case sensitive!
        MESSAGE1 = fstring_message1.encode()
        MESSAGE2 = fstring_message2.encode()
        MESSAGE3 = fstring_message3.encode()

        # use the socket sendto() method to send the message
        sock.sendto(MESSAGE1, address_tuple)
        sock.sendto(MESSAGE2, address_tuple)
        sock.sendto(MESSAGE3, address_tuple)

        # sleep for a few seconds (slowly read from file)
        time.sleep(1)

# when indented under the row for row code, it sends each row of the csv as a separate message/task.
        try:
            # create a connection to the RabbitMQ server and a channel
            conn = pika.BlockingConnection(pika.ConnectionParameters(host))
            ch = conn.channel()
            # use the channel to declare a durable queue
            # a durable queue will survive a RabbitMQ server restart
            # and help ensure messages are processed in order
            # messages will not be deleted until the consumer acknowledges
            ch.queue_declare(queue=queue_name, durable=True)
            # use the channel to publish a message to the queue; each message passes through an exchange
            ch.basic_publish(exchange="", routing_key=queue_name, body=MESSAGE1)
            ch.basic_publish(exchange="", routing_key=queue_name, body=MESSAGE2)
            ch.basic_publish(exchange="", routing_key=queue_name, body=MESSAGE3)
            # print a message to the console for the user
            print(f" [x] Sent {MESSAGE1}")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error: Connection to RabbitMQ server failed: {e}")
            sys.exit(1)
        finally:
            # close the connection to the server
            conn.close()

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    # ask the user if they'd like to open the RabbitMQ Admin site
    # show_offer variable is set to False/off for RabbitMQ site
    show_offer = True
    offer_rabbitmq_admin_site(show_offer)
    # get the message from the command line
    # if no arguments are provided, use the default message
    # use the join method to convert the list of arguments into a string
    # join by the space character inside the quotes
    message1 = " ".join(sys.argv[1:])  or "{message1}"
    message2 = " ".join(sys.argv[1:])  or "{message2}"
    message3 = " ".join(sys.argv[1:])  or "{message3}"
    # send the message to the queue
    send_message("localhost","01-smoker",message1)
    send_message("localhost","02-food-A",message2)
    send_message("localhost","03-food-B",message3)
