/**
 * aMule — Net Storage Adapter
 *
 * Bridge between aMule and Net Protocol Storage.
 *
 * IMPORTANT:
 * This first version is intentionally read/prepare only.
 * It does NOT sign or broadcast blockchain transactions.
 *
 * The next step will add the wallet/transaction layer.
 */

import {
    StorageClient,
    processDataForStorage,
    OPTIMAL_CHUNK_SIZE,
} from "@net-protocol/storage";


/**
 * =========================================================
 * CONFIGURATION
 * =========================================================
 */

const NET_CHAIN_ID = Number(
    process.env.NET_CHAIN_ID || 8453
);

const NET_RPC_URL =
    process.env.NET_RPC_URL || undefined;


/**
 * =========================================================
 * STORAGE CLIENT
 * =========================================================
 */

const clientOptions = {
    chainId: NET_CHAIN_ID,
};

if (NET_RPC_URL) {
    clientOptions.overrides = {
        rpcUrls: [NET_RPC_URL],
    };
}

const client = new StorageClient(
    clientOptions
);


/**
 * =========================================================
 * RESOURCE KEY
 * =========================================================
 *
 * aMule uses the encrypted SHA-256 resource ID
 * as the deterministic storage key.
 */

export function createStorageKey(
    resourceId
) {
    if (
        typeof resourceId !== "string" ||
        resourceId.length !== 64
    ) {
        throw new Error(
            "Invalid aMule resource ID."
        );
    }

    return `amule:${resourceId}`;
}


/**
 * =========================================================
 * PREPARE RESOURCE
 * =========================================================
 *
 * Prepares encrypted resource data for Net Storage.
 *
 * This function does not broadcast anything.
 */

export function prepareResource(
    resourceId,
    encryptedData,
    operatorAddress
) {
    if (!operatorAddress) {
        throw new Error(
            "Operator address is required."
        );
    }

    if (!Buffer.isBuffer(encryptedData)) {
        throw new Error(
            "encryptedData must be a Buffer."
        );
    }

    const storageKey =
        createStorageKey(resourceId);

    const base64Data =
        encryptedData.toString("base64");

    const dataUri =
        `data:application/octet-stream;base64,${base64Data}`;

    const processed =
        processDataForStorage(
            dataUri,
            operatorAddress,
            storageKey,
            OPTIMAL_CHUNK_SIZE
        );

    return {
        resourceId,
        storageKey,
        operatorAddress,
        chainId: NET_CHAIN_ID,
        size: encryptedData.length,
        processed,
    };
}


/**
 * =========================================================
 * READ RESOURCE
 * =========================================================
 *
 * Reads a resource from Net Storage.
 *
 * This is useful after a resource has already been
 * published on-chain.
 */

export async function readResource(
    resourceId,
    operatorAddress
) {
    if (!operatorAddress) {
        throw new Error(
            "Operator address is required."
        );
    }

    const storageKey =
        createStorageKey(resourceId);

    const result =
        await client.getViaRouter({
            key: storageKey,
            operator: operatorAddress,
        });

    return {
        resourceId,
        storageKey,
        operatorAddress,
        chainId: NET_CHAIN_ID,
        data: result,
    };
}


/**
 * =========================================================
 * HEALTH CHECK
 * =========================================================
 */

export function getNetStorageInfo() {
    return {
        provider: "Net Protocol",
        chainId: NET_CHAIN_ID,
        storage: "Net Storage",
        sdk: "@net-protocol/storage",
        status: "configured",
    };
}


/**
 * =========================================================
 * CLI TEST
 * =========================================================
 */

if (
    process.argv[1] &&
    process.argv[1].endsWith("storage.js")
) {
    console.log(
        "aMule Net Storage Adapter"
    );

    console.log(
        getNetStorageInfo()
    );
}
