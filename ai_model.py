import json
import os
from datetime import datetime
import logging

import cml.data_v1 as cmldata
from openai import OpenAI

logging.getLogger().setLevel(logging.INFO)

SPARK_DATA_LAKE_CONNECTION = os.getenv("SPARK_DATA_LAKE_CONNECTION")
DEMO_DATABASE_NAME = os.getenv("DEMO_DATABASE_NAME")
DEMO_TABLE_NAME = os.getenv("DEMO_TABLE_NAME")

data_lake_connection = cmldata.get_connection(SPARK_DATA_LAKE_CONNECTION)
spark = data_lake_connection.get_spark_session()

# openai client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieveCustomerInfo(name: str, dob: str, address: str) -> dict | bool:
    """
    Retrieve customer information from the database based on provided details.

    This function executes a SQL query to fetch customer details, using the
    customer's name, date of birth, and address as filters. The query results
    are returned as a dictionary mapping column names to their corresponding values.
    If no matching records are found, the function returns False.

    Example:
        name = 'Alex'
        dob = '1990-03-13'
        address = 'Sample Street 1'

    Parameters:
        name (str): The name of the customer.
        dob (str): The date of birth of the customer in 'YYYY-MM-DD' format.
        address (str): The address of the customer.

    Returns:
        dict: A dictionary containing customer information if a match is found.
        bool: False if no matching customer is found.
    """

    logging.info(f"retrieveCustomerInfo called with name: {name}, dob: {dob}, address: {address}.")

    sql_query = f"""
    SELECT
        name,
        customer_id as Customer_ID,
        current_product as Current_Product,
        churn_risk as Churn_Risk,
        customer_since as Customer_Since,
        date_of_birth as Date_of_birth,
        address as Address,
        preapproved_for_discount as Preappoved_for_discount
    FROM {DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}
    WHERE LOWER(name) = LOWER('{name}')
    AND date_of_birth = '{dob}'
    AND LOWER(address) = LOWER('{address}')
    """

    logging.info(f"Attempting to run query: {sql_query}.")

    results_dataframe = spark.sql(sql_query)
    results_values = results_dataframe.collect()
    if results_values:
        results_context = dict(zip(results_dataframe.columns, results_values[0]))
        logging.info(f"Customer information retrieved: {results_context}.")
        return results_context
    else:
        logging.info(f"No matching customer found.")
        return False


def is_valid_date(date_str: str):
    try:
        # Attempt to parse the string into a datetime object
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        # If parsing fails, it's not a valid date
        return False


def predict(data: dict[str, str]) -> dict:
    """
    Predicts outcomes based on the provided task and text data using an AI model.

    This function processes input data to perform specific tasks such as providing
    AI assistance, summarizing conversations, or retrieving customer information.
    It validates the input data, executes the appropriate task using the OpenAI
    model, and returns the results in a structured format.

    Parameters:
        data (dict[str, str]): A dictionary containing 'text' and 'task' keys. The
        'text' key holds the conversation text, and the 'task' key specifies the
        operation to perform ('ai_help', 'summarize', or 'getCustomerInfo').

    Returns:
        dict: A dictionary containing the prediction results, which may include
        recommendation text, customer information, and a flag indicating whether
        customer information was found.
        
    Raises:
        TypeError: If the input data is not a dictionary or lacks required keys,
        or if the values for 'text' or 'task' are not strings.
    """

    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if "text" not in data:
        raise TypeError("data must contain a key of 'text'")

    if "task" not in data:
        raise TypeError("data must contain a key of 'task'")

    task = data['task']
    if not isinstance(task, str):
        raise TypeError("text must be a string")

    text = data["text"]
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if task == 'ai_help':
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are helping a call center worker for a telco company called airwave. You will receive the user text content, which will include the call center worker and the customers spoken words converted to text. You are called upon when teh call center agent needs some sort of help, like details about the available products or suggestions for troubleshooting etc. It is your job to provide helpful suggestions. Make sure they are short so the call center worker can easily look at them and read them out to the customer. Do not include multiple suggestions, just one with enough information that the call center agent can use. If the call center agend mentions they are looking for some information, or the customer sais they need additional information, provide that information (if available) in your response. You may receive additional information about the customer such as name and currently used products. The company has currently has 3 products: " + """
                AirSpeed Advanced
                High Speed Wireless Broadband

                Special Offer € 45 per month
                Cost is € 45 p/m for the first 3 months and € 60 thereafter
                12 Month contract
                Up to 70 Mbps / 7 Mbps

                FREE Fritzbox Router
                Installation fee of € 150
                Optional Home Phone Service

                and

                AirSpeed Plus
                High Speed Wireless Broadband

                Special Offer € 35 per month
                Cost is € 35 p/m for the first 3 months and € 50 thereafter
                12 Month contract
                Up to 50 Mbps / 5 Mbps

                FREE Fritzbox Router
                Installation fee of € 150
                Optional Home Phone Service

                and

                AirSpeed Home
                High Speed Wireless Broadband

                Special Offer € 25 per month
                Cost is € 25 p/m for the first 3 months and € 40 thereafter
                12 Month contract
                Up to 30 Mbps / 3 Mbps

                FREE Fritzbox Router
                Installation fee of €150
                Optional Home Phone Service  

                There are currently no active promotions other than the one's mentioned above. There is an option to give customers a discount of 5 percent but only if they sign up for a 2 year contract. This should only be offered to customers that are at risk of churning (churn_risk 1 or 2) or have very negative conversations.         
                """},
                {"role": "user", "content": f"{text}"}
            ]
        )

        output = {"recommendationText": completion.choices[0].message.content}

    if task == 'summarize':
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are helping a call center worker for a telco company called airwave. You will receive the user text content, which will include the call center worker and the customers spoken words converted to text. You are called at the end of a conversation to summarize the call. Make sure the summary is as short as possible but always includes all relevant parts of the conversation. You may receive information about the customer such as name and currently used products. The company has currently has 3 products: " + """
                AirSpeed Advanced
                High Speed Wireless Broadband

                Special Offer € 45 per month
                Cost is € 45 p/m for the first 3 months and € 60 thereafter
                12 Month contract
                Up to 70 Mbps / 7 Mbps

                FREE Fritzbox Router
                Installation fee of € 150
                Optional Home Phone Service

                and

                AirSpeed Plus
                High Speed Wireless Broadband

                Special Offer € 35 per month
                Cost is € 35 p/m for the first 3 months and € 50 thereafter
                12 Month contract
                Up to 50 Mbps / 5 Mbps

                FREE Fritzbox Router
                Installation fee of € 150
                Optional Home Phone Service

                and

                AirSpeed Home
                High Speed Wireless Broadband

                Special Offer € 25 per month
                Cost is € 25 p/m for the first 3 months and € 40 thereafter
                12 Month contract
                Up to 30 Mbps / 3 Mbps

                FREE Fritzbox Router
                Installation fee of €150
                Optional Home Phone Service

                Summarize the converastion short but include all important information.             
                """},
                {"role": "user", "content": f"{text}"}
            ]
        )

        output = {"recommendationText": completion.choices[0].message.content}

    if task == 'getCustomerInfo':
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": 'You are a helpful assistant for call center agents designed to analyze text from a conversation and figure out information about the customer who is calling outputing a JSON. Provide your answer in JSON structure like this {"name": "<The name of the customer>", "address": "<The street of the customer> <The house number of the customer as number, not string>", "dob": "<The date of birth of the customer as YYYY-MM-DD>". You will be given the entire conversation so far, do not worry if the information is not complete yet, just fill out whatever you can identify.'},
                {"role": "user", "content": f"{text}"}
            ]
        )

        info = json.loads(completion.choices[0].message.content)
        info_complete = False
        needed_informattion = ['name', 'address', 'dob']

        for info_elem in needed_informattion:
            if info_elem in info and info[info_elem] and info[info_elem] != "":
                info_complete = True
                if info_elem == 'dob' and not is_valid_date(info['dob']):
                    info_complete = False
            else:
                info_complete = False

        if info_complete:
            customer_info_from_db = retrieveCustomerInfo(info['name'], info['dob'], info['address'])
            if customer_info_from_db == False:
                output = {"recommendationText": completion.choices[0].message.content,
                          "foundCustomer": 0}
            else:
                output = {"recommendationText": completion.choices[0].message.content,
                          "foundCustomer": 1,
                          "customerInfo": customer_info_from_db}

        else:
            output = {
                "recommendationText": completion.choices[0].message.content}

    return output
