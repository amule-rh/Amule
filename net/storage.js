/**
 * aMule — Net Storage Adapter
 *
 * Bridge between aMule and Net Protocol Storage.
 *
 * This module handles:
 * - Net Storage client configuration
 * - aMule storage keys
 * - resource preparation
 * - resource retrieval
 *
 * Blockchain writes are intentionally isolated.
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
 *
 * NET_CHAIN_ID must be supplied through the environment.
 *
 * We do NOT hard-code Base or Robinhood Chain here because
 * Net Protocol is multi-chain.
 */

const NET_CHAIN_ID =
    Number(process.env.NET_CHAIN_ID);


if (!NET_CHAIN_ID) {
    throw new Error(
        "NET_CHAIN_ID environment variable is required."
    );
}


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
 * Converts encrypted aMule data into the format expected
 * by Net Storage.
 *
 * This does NOT broadcast a blockchain transaction.
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
 * Reads a resource through Net Storage Router.
 *
 * This supports resources that require chunked
 * storage resolution.
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
 * READ RESOURCE BY KEY
 * =========================================================
 *
 * Useful when aMule discovers a resource belonging
 * to another Net operator.
 */

export async function readResourceByKey(
    storageKey,
    operatorAddress
) {
    if (!operatorAddress) {
        throw new Error(
            "Operator address is required."
        );
    }


    if (!storageKey) {
        throw new Error(
            "Storage key is required."
        );
    }


    return await client.getViaRouter({
        key: storageKey,
        operator: operatorAddress,
    });
}


/**
 * =========================================================
 * NET STORAGE INFO
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
