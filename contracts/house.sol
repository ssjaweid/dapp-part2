pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract RealEstateRegistry is ERC721Full {
    constructor() public ERC721Full("RealEstateToken", "RESTATE") {}

    struct Property {
        string location;
        string ownerName;
        uint256 estimatedValue;
        uint256 squareFeet;
        string propertyJson;
    }    

    mapping(uint256 => Property) public propertyCollection;

    event Appraisal(uint256 tokenId, uint256 newAppraisalValue, string reportURI, string propertyJson);

    function getPropertyDetails(uint256 tokenId) public view returns (string memory detailsJson) {
        return propertyCollection[tokenId].propertyJson;
    }

    function registerProperty(
        address ownerAddress,
        string memory location,
        string memory ownerName,
        uint256 initialEstimatedValue,
        uint256 squareFeet,
        string memory tokenURI,
        string memory propertyJSON
    ) public returns (uint256) {
        uint256 tokenId = totalSupply();

        _mint(ownerAddress, tokenId);
        _setTokenURI(tokenId, tokenURI);

        propertyCollection[tokenId] = Property(location, ownerName, initialEstimatedValue, squareFeet, propertyJSON);

        return tokenId;
    }    

    function newAppraisal(
        uint256 tokenId,
        uint256 newEstimatedValue,
        string memory reportURI,
        string memory propertyJSON
    ) public returns (uint256) {
        propertyCollection[tokenId].estimatedValue = newEstimatedValue;

        emit Appraisal(tokenId, newEstimatedValue, reportURI, propertyJSON);

        return propertyCollection[tokenId].estimatedValue;
    }
}