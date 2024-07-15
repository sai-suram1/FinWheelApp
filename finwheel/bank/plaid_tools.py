import plaid
import base64
# Replace with your Plaid client ID and secret (obtained from Plaid)
PLAID_CLIENT_ID = '64c1ec037d2ab20018140136'
PLAID_SECRET = '95fa3dcd4922068b9c8e9fdcb5fa3b'

# Initialize the Plaid client
client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, environment='sandbox')  # Use 'production' for live environments

def get_plaid_processor_token(user_id):
    """
    Prompts the user to initiate Plaid Link flow and retrieves a processor token.

    Args:
        user_id (str): The unique identifier for the current user.

    Returns:
        str: The processor token obtained through Plaid Link, or None if the process is cancelled.
    """

    # Replace with the product(s) you want to use (e.g., 'transactions', 'identity')
    PRODUCTS = ['transactions']

    # Replace with your Plaid Link public key (obtained from Plaid)
    PLAID_LINK_PUBLIC_KEY = 'YOUR_PLAID_LINK_PUBLIC_KEY'

    # Open Plaid Link flow in the user's browser
    link_token_create_response = client.Link.Token.create(
        user={'client_user_id': user_id},
        products=PRODUCTS,
        client_name='Your Application Name',
        country='US',
        language='en'
    )

    if link_token_create_response['status'] == 'succeeded':
        link_token = link_token_create_response['link_token']

        # User interaction to initiate Plaid Link (replace with your preferred method)
        print('Please open the following link in your browser to connect your bank account:')
        print(f'https://{client.environment}/link/{link_token}')

        # Replace with your mechanism to wait for the user to complete Plaid Link
        # (e.g., polling for an exchange token or using Plaid webhooks)
        exchange_token = input('Enter the exchange token obtained from Plaid Link (or leave blank to cancel): ')

        if exchange_token:
            # Exchange the Plaid Link exchange token for a processor token
            exchange_token_response = client.Item.ExchangeToken(exchange_token)

            if exchange_token_response['status'] == 'succeeded':
                return exchange_token_response['access_token']
            else:
                print('Error exchanging Plaid Link token:', exchange_token_response['error'])
                return None
        else:
            print('Plaid Link flow cancelled.')
            return None
    else:
        print('Error creating Plaid Link token:', link_token_create_response['error'])
        return None


processor = get_plaid_processor_token(PLAID_CLIENT_ID)
print(processor)


def initiate_ach_funding(user_id, processor_token):
    """
    Initiates ACH funding using Alpaca's API and the provided processor token.

    Args:
        user_id (str): The unique identifier for the current user.
        processor_token (str): The processor token obtained through Plaid Link.

    Returns:
        dict: The response from Alpaca's ACH funding API, or None if an error occurs.
    """

    # Replace with your Alpaca API key and secret (obtained from Alpaca)
    ALPACA_API_KEY = 'YOUR_ALPACA_API_KEY'
    ALPACA_API_SECRET = 'YOUR_ALPACA_API_SECRET'

    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{ALPACA_API_KEY}:{ALPACA_API_SECRET}".encode("utf-8")).decode("utf-8")}'
    }

    # Replace with the Alpaca API endpoint for ACH funding (consult Alpaca's documentation)
    ach_funding_url = 'https://api.alpaca.markets/v2/ach/transfers'

    data = {
        'account_id': 'YOUR_ALPACA_ACCOUNT_ID',  # Replace with your Alpaca account ID
        'ach_class': 'plaid',  # Indicate ACH funding via Plaid
        'routing_number': None,  #
    }
