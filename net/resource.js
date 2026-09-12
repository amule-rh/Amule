/**
 * aMule — Net Resource Model
 *
 * Defines the metadata required to discover and retrieve
 * resources stored through Net Protocol.
 *
 * aMule resources are not necessarily owned by aMule.
 * They can belong to any Net Storage operator.
 */

export function createResourceRecord({
    resourceId,
    operator,
    storageKey,
    filename = null,
    contentType = "application/octet-stream",
    size = 0,
    encrypted = true,
}) {
    if (!resourceId) {
        throw new Error("resourceId is required.");
    }

    if (!operator) {
        throw new Error("operator is required.");
    }

    if (!storageKey) {
        throw new Error("storageKey is required.");
    }

    return {
        protocol: "amule",
        version: 1,

        resourceId,

        storage: {
            provider: "net",
            operator,
            key: storageKey,
        },

        metadata: {
            filename,
            contentType,
            size,
            encrypted,
        },
    };
}


/**
 * Validate an aMule resource record.
 */

export function validateResourceRecord(record) {
    if (!record) {
        return false;
    }

    if (record.protocol !== "amule") {
        return false;
    }

    if (record.version !== 1) {
        return false;
    }

    if (!record.resourceId) {
        return false;
    }

    if (!record.storage) {
        return false;
    }

    if (record.storage.provider !== "net") {
        return false;
    }

    if (!record.storage.operator) {
        return false;
    }

    if (!record.storage.key) {
        return false;
    }

    return true;
}


/**
 * Convert a resource record to JSON.
 */

export function serializeResourceRecord(record) {
    if (!validateResourceRecord(record)) {
        throw new Error(
            "Invalid aMule resource record."
        );
    }

    return JSON.stringify(
        record,
        null,
        2
    );
}
