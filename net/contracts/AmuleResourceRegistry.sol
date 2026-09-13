// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * aMule Resource Registry
 *
 * resourceId = stable logical resource identifier.
 * contentHash = hash of the current exact content bytes.
 *
 * Updating a resource changes its content hash/version while retaining
 * the logical resource ID.
 */
contract AmuleResourceRegistry {
    struct Resource {
        bytes32 resourceId;
        address owner;
        bytes32 contentHash;
        string storageRef;
        string contentType;
        string source;
        uint64 createdAt;
        uint64 updatedAt;
        uint32 version;
        bool active;
    }

    mapping(bytes32 => Resource) private resources;
    mapping(address => bytes32[]) private ownerResources;

    error ResourceAlreadyExists(bytes32 resourceId);
    error ResourceNotFound(bytes32 resourceId);
    error NotResourceOwner(bytes32 resourceId);
    error InvalidResourceId();
    error InvalidContentHash();
    error EmptyStorageReference();
    error InactiveResource(bytes32 resourceId);

    event ResourcePublished(
        bytes32 indexed resourceId,
        address indexed owner,
        bytes32 indexed contentHash,
        string storageRef,
        string contentType,
        string source,
        uint32 version
    );

    event ResourceUpdated(
        bytes32 indexed resourceId,
        bytes32 indexed contentHash,
        string storageRef,
        uint32 version
    );

    event ResourceDeactivated(bytes32 indexed resourceId);

    function publishResource(
        bytes32 resourceId,
        bytes32 contentHash,
        string calldata storageRef,
        string calldata contentType,
        string calldata source
    ) external {
        if (resourceId == bytes32(0)) revert InvalidResourceId();
        if (contentHash == bytes32(0)) revert InvalidContentHash();
        if (bytes(storageRef).length == 0) revert EmptyStorageReference();
        if (resources[resourceId].createdAt != 0) {
            revert ResourceAlreadyExists(resourceId);
        }

        Resource memory resource = Resource({
            resourceId: resourceId,
            owner: msg.sender,
            contentHash: contentHash,
            storageRef: storageRef,
            contentType: contentType,
            source: source,
            createdAt: uint64(block.timestamp),
            updatedAt: uint64(block.timestamp),
            version: 1,
            active: true
        });

        resources[resourceId] = resource;
        ownerResources[msg.sender].push(resourceId);

        emit ResourcePublished(
            resourceId,
            msg.sender,
            contentHash,
            storageRef,
            contentType,
            source,
            1
        );
    }

    function updateResource(
        bytes32 resourceId,
        bytes32 contentHash,
        string calldata storageRef
    ) external {
        if (contentHash == bytes32(0)) revert InvalidContentHash();

        Resource storage resource = resources[resourceId];
        if (resource.createdAt == 0) revert ResourceNotFound(resourceId);
        if (resource.owner != msg.sender) revert NotResourceOwner(resourceId);
        if (!resource.active) revert InactiveResource(resourceId);
        if (bytes(storageRef).length == 0) revert EmptyStorageReference();

        resource.contentHash = contentHash;
        resource.storageRef = storageRef;
        resource.updatedAt = uint64(block.timestamp);
        resource.version += 1;

        emit ResourceUpdated(
            resourceId,
            contentHash,
            storageRef,
            resource.version
        );
    }

    function deactivateResource(bytes32 resourceId) external {
        Resource storage resource = resources[resourceId];
        if (resource.createdAt == 0) revert ResourceNotFound(resourceId);
        if (resource.owner != msg.sender) revert NotResourceOwner(resourceId);

        resource.active = false;
        resource.updatedAt = uint64(block.timestamp);

        emit ResourceDeactivated(resourceId);
    }

    function getResource(bytes32 resourceId)
        external
        view
        returns (Resource memory)
    {
        Resource memory resource = resources[resourceId];
        if (resource.createdAt == 0) revert ResourceNotFound(resourceId);
        return resource;
    }

    function resourceExists(bytes32 resourceId) external view returns (bool) {
        return resources[resourceId].createdAt != 0;
    }

    function isResourceActive(bytes32 resourceId) external view returns (bool) {
        return resources[resourceId].createdAt != 0 && resources[resourceId].active;
    }

    function getResourcesByOwner(address owner)
        external
        view
        returns (bytes32[] memory)
    {
        return ownerResources[owner];
    }

    function getResourceVersion(bytes32 resourceId)
        external
        view
        returns (uint32)
    {
        Resource memory resource = resources[resourceId];
        if (resource.createdAt == 0) revert ResourceNotFound(resourceId);
        return resource.version;
    }
}
