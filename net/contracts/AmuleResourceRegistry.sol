// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * aMule Net
 *
 * Decentralized Resource Registry
 *
 * The registry stores the verifiable identity and metadata
 * required to discover resources in the aMule network.
 *
 * The actual resource content is NOT stored here.
 *
 * Blockchain stores:
 * - resource identity
 * - content hash
 * - owner/operator
 * - storage reference
 * - content type
 * - source/provenance
 * - timestamps
 * - versions
 *
 * Content is stored through an external storage layer.
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
        uint32 version,
        uint64 timestamp
    );

    event ResourceUpdated(
        bytes32 indexed resourceId,
        address indexed owner,
        bytes32 indexed contentHash,
        string storageRef,
        string contentType,
        string source,
        uint32 version,
        uint64 timestamp
    );

    event ResourceDeactivated(
        bytes32 indexed resourceId,
        address indexed owner,
        uint64 timestamp
    );

    /**
     * Publish a new resource.
     */
    function publishResource(
        bytes32 resourceId,
        bytes32 contentHash,
        string calldata storageRef,
        string calldata contentType,
        string calldata source
    )
        external
    {
        if (resourceId == bytes32(0)) {
            revert InvalidResourceId();
        }

        if (contentHash == bytes32(0)) {
            revert InvalidContentHash();
        }

        if (
            bytes(storageRef).length == 0
        ) {
            revert EmptyStorageReference();
        }

        if (
            resources[resourceId].createdAt != 0
        ) {
            revert ResourceAlreadyExists(
                resourceId
            );
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

        ownerResources[msg.sender].push(
            resourceId
        );

        emit ResourcePublished(
            resourceId,
            msg.sender,
            contentHash,
            storageRef,
            contentType,
            source,
            1,
            uint64(block.timestamp)
        );
    }

    /**
     * Update an existing resource.
     *
     * Only the original resource owner
     * can update it.
     *
     * Updating creates a new resource version.
     */
    function updateResource(
        bytes32 resourceId,
        bytes32 contentHash,
        string calldata storageRef,
        string calldata contentType,
        string calldata source
    )
        external
    {
        Resource storage resource =
            resources[resourceId];

        if (
            resource.createdAt == 0
        ) {
            revert ResourceNotFound(
                resourceId
            );
        }

        if (
            resource.owner != msg.sender
        ) {
            revert NotResourceOwner(
                resourceId
            );
        }

        if (
            !resource.active
        ) {
            revert InactiveResource(
                resourceId
            );
        }

        if (
            contentHash == bytes32(0)
        ) {
            revert InvalidContentHash();
        }

        if (
            bytes(storageRef).length == 0
        ) {
            revert EmptyStorageReference();
        }

        resource.contentHash =
            contentHash;

        resource.storageRef =
            storageRef;

        resource.contentType =
            contentType;

        resource.source =
            source;

        resource.updatedAt =
            uint64(block.timestamp);

        resource.version += 1;

        emit ResourceUpdated(
            resourceId,
            msg.sender,
            contentHash,
            storageRef,
            contentType,
            source,
            resource.version,
            uint64(block.timestamp)
        );
    }

    /**
     * Deactivate a resource.
     *
     * The resource remains permanently recorded
     * but is no longer considered active.
     */
    function deactivateResource(
        bytes32 resourceId
    )
        external
    {
        Resource storage resource =
            resources[resourceId];

        if (
            resource.createdAt == 0
        ) {
            revert ResourceNotFound(
                resourceId
            );
        }

        if (
            resource.owner != msg.sender
        ) {
            revert NotResourceOwner(
                resourceId
            );
        }

        resource.active = false;

        resource.updatedAt =
            uint64(block.timestamp);

        emit ResourceDeactivated(
            resourceId,
            msg.sender,
            uint64(block.timestamp)
        );
    }

    /**
     * Retrieve a resource.
     */
    function getResource(
        bytes32 resourceId
    )
        external
        view
        returns (
            Resource memory
        )
    {
        if (
            resources[resourceId].createdAt == 0
        ) {
            revert ResourceNotFound(
                resourceId
            );
        }

        return resources[resourceId];
    }

    /**
     * Check whether a resource exists.
     */
    function resourceExists(
        bytes32 resourceId
    )
        external
        view
        returns (bool)
    {
        return (
            resources[resourceId].createdAt != 0
        );
    }

    /**
     * Check whether a resource is active.
     */
    function isResourceActive(
        bytes32 resourceId
    )
        external
        view
        returns (bool)
    {
        Resource storage resource =
            resources[resourceId];

        return (
            resource.createdAt != 0
            && resource.active
        );
    }

    /**
     * Get all resource IDs belonging
     * to an owner.
     */
    function getResourcesByOwner(
        address owner
    )
        external
        view
        returns (
            bytes32[] memory
        )
    {
        return ownerResources[owner];
    }

    /**
     * Get the current version of a resource.
     */
    function getResourceVersion(
        bytes32 resourceId
    )
        external
        view
        returns (uint32)
    {
        if (
            resources[resourceId].createdAt == 0
        ) {
            revert ResourceNotFound(
                resourceId
            );
        }

        return resources[resourceId].version;
    }
}
