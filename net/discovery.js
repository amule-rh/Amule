/**
 * aMule — Net Resource Discovery
 *
 * Discovers resources stored by any Net Protocol operator.
 *
 * aMule is not limited to resources created by its own wallet.
 */

import { StorageClient } from "@net-protocol/storage";


const NET_CHAIN_ID = Number(
    process.env.NET_CHAIN_ID || 8453
);


const NET_RPC_URL =
    process.env.NET_RPC_URL || undefined;


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
 * Discover all storage keys belonging to an operator.
 *
 * This is the first step for discovering resources
 * published by another aMule user.
 */
export async function discoverOperator(
    operatorAddress
) {
    if (!operatorAddress) {
        throw new Error(
            "Operator address is required."
        );
    }

    return await client.getForOperator({
        operator: operatorAddress,
    });
}


/**
 * Retrieve one specific resource from an operator.
 */
export async function discoverResource(
    operatorAddress,
    storageKey
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

    return await client.getForOperatorAndKey({
        operator: operatorAddress,
        key: storageKey,
    });
}


/**
 * Read a resource through the Net Storage Router.
 *
 * The router can resolve regular/chunked storage.
 */
export async function retrieveResource(
    operatorAddress,
    storageKey
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
        operator: operatorAddress,
        key: storageKey,
    });
}


/**
 * Return Net discovery configuration.
 */
export function getDiscoveryInfo() {
    return {
        provider: "Net Protocol",
        chainId: NET_CHAIN_ID,
        status: "ready",
    };
}
