import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

# Load environment variables
load_dotenv()

# Connect to Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Load the contract
@st.cache_resource()
def load_contract():
    with open(Path('./contracts/compiled/houseregistry_abi.json')) as f:
        contract_abi = json.load(f)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
    return w3.eth.contract(address=contract_address, abi=contract_abi)

contract = load_contract()

# Helper functions for pinning
def pin_house_data(name, file):
    ipfs_file_hash = pin_file_to_ipfs(file.getvalue())
    token_json = {
        "name": name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)
    json_ipfs_hash = pin_json_to_ipfs(json_data)
    return json_ipfs_hash, token_json


# Main Streamlit UI
st.title("Real Estate Registration System")
st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")

# Register New Property
st.markdown("## Register New Property")
house_name = st.text_input("Enter the name of the property")
house_address = st.text_input("Enter the property address")
owner_name = st.text_input("Enter the owner's name")
house_value = st.text_input("Enter the property value")
square_feet = st.text_input("Enter the square footage of the property")
file = st.file_uploader("Upload House Image", type=["jpg", "jpeg", "png"])

if st.button("Register Property"):
    house_ipfs_hash, token_json = pin_house_data(house_name, file)
    house_uri = f"ipfs://{house_ipfs_hash}"

    tx_hash = contract.functions.registerProperty(
        address,                # ownerAddress
        house_address,          # location
        owner_name,             # ownerName
        int(house_value),       # initialEstimatedValue
        int(square_feet),       # squareFeet
        house_uri,              # tokenURI
        token_json['image']     # propertyJSON
    ).transact({'from': address, 'gas': 1000000})
    
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.markdown(f"[Property IPFS Gateway Link](https://ipfs.io/ipfs/{house_ipfs_hash})")
    st.markdown(f"[Property IPFS Image Link](https://ipfs.io/ipfs/{token_json['image']})")

st.markdown("---")


# Fetch total number of properties/tokens
total_properties = contract.functions.totalSupply().call()
property_ids = list(range(total_properties))

# Appraise Property
st.markdown("## Appraise Property")
property_id = st.selectbox("Choose a Property ID", property_ids)
new_property_value = st.text_input("Enter the new property value")
appraisal_report = st.text_area("Enter details for the Appraisal Report")

if st.button("Appraise Property"):
    property_json = contract.functions.getPropertyDetails(property_id).call()

    if isinstance(appraisal_report, str) and isinstance(property_json, str):
        appraisal_data = convert_data_to_json(appraisal_report + property_json)
    else:
        st.write("Error: Appraisal report or property details are not valid strings.")

    appraisal_data = convert_data_to_json(appraisal_report + property_json)
    appraisal_report_ipfs_hash = pin_json_to_ipfs(appraisal_data)
    report_uri = f"ipfs://{appraisal_report_ipfs_hash}"

    tx_hash = contract.functions.newAppraisal(
        property_id,
        int(new_property_value),
        report_uri,
        property_json
    ).transact({"from": w3.eth.accounts[0]})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write(receipt)

st.markdown("---")

# Get Appraisals
st.markdown("## Get the appraisal report history")
property_token_id = st.number_input("Property ID", value=0, step=1)
if st.button("Get Appraisal Reports"):
    appraisal_filter = contract.events.Appraisal.createFilter(fromBlock=0, argument_filters={"tokenId": property_token_id})
    reports = appraisal_filter.get_all_entries()

    if reports:
        for report in reports:
            st.markdown("### Appraisal Report Event Log")
            st.write(dict(report))
            report_uri = dict(report)["args"]["reportURI"]
            report_ipfs_hash = report_uri[7:]
            st.markdown(f"[IPFS Gateway Link for Appraisal](https://ipfs.io/ipfs/{report_ipfs_hash})")
            st.image(f'https://ipfs.io/ipfs/{dict(report)["args"]["propertyJson"]}')
    else:
        st.write("This property has no new appraisals")


