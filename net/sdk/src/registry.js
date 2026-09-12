/**
 * aMule Net — Resource Registry SDK
 *
 * Client for interacting with the aMule
 * Resource Registry smart contract.
 */

import {
    createPublicClient,
    createWalletClient,
    http,
} from "viem";

import {
    privateKeyToAccount,
} from "viem/accounts";


export const ROBINHOOD_TESTNET = {
    id: 46630,

    name: "Robinhood Chain Testnet",

    nativeCurrency: {
        name: "Ether",
        symbol: "ETH",
        decimals: 18,
    },

    rpcUrls: {
        default: {
            http: [
                "https://rpc.testnet.chain.robinhood.com",
            ],
        },
    },
};


export const REGISTRY_ABI = [
    {
        type: "function",
        name: "publishResource",
        stateMutability: "nonpayable",

        inputs: [
            {
                name: "resourceId",
                type: "bytes32",
            },
            {
                name: "contentHash",
                type: "bytes32",
            },
            {
                name: "storageRef",
                type: "string",
            },
            {
                name: "contentType",
                type: "string",
            },
            {
                name: "source",
                type: "string",
            },
        ],

        outputs: [],
    },

    {
        type: "function",
        name: "getResource",

        stateMutability: "view",

        inputs: [
            {
                name: "resourceId",
                type: "bytes32",
            },
        ],

        outputs: [
            {
                name: "resource",
                type: "tuple",

                components: [
                    {
                        name: "resourceId",
                        type: "bytes32",
                    },
                    {
                        name: "owner",
                        type: "address",
                    },
                    {
                        name: "contentHash",
                        type: "bytes32",
                    },
                    {
                        name: "storageRef",
                        type: "string",
                    },
                    {
                        name: "contentType",
                        type: "string",
                    },
                    {
                        name: "source",
                        type: "string",
                    },
                    {
                        name: "createdAt",
                        type: "uint64",
                    },
                    {
                        name: "updatedAt",
                        type: "uint64",
                    },
                    {
                        name: "version",
                        type: "uint32",
                    },
                    {
                        name: "active",
                        type: "bool",
                    },
                ],
            },
        ],
    },

    {
        type: "function",
        name: "resourceExists",

        stateMutability: "view",

        inputs: [
            {
                name: "resourceId",
                type: "bytes32",
            },
        ],

        outputs: [
            {
                name: "",
                type: "bool",
            },
        ],
    },

    {
        type: "function",
        name: "getResourcesByOwner",

        stateMutability: "view",

        inputs: [
            {
                name: "owner",
                type: "address",
            },
        ],

        outputs: [
            {
                name: "",
                type: "bytes32[]",
            },
        ],
    },
];


export function createRegistryClient(
    contractAddress,
) {
    if (!contractAddress) {
        throw new Error(
            "Registry contract address is required.",
        );
    }

    return createPublicClient({
        chain: ROBINHOOD_TESTNET,

        transport: http(
            ROBINHOOD_TESTNET.rpcUrls
                .default
                .http[0],
        ),
    });
}


export async function getResource(
    client,
    contractAddress,
    resourceId,
) {
    if (!client) {
        throw new Error(
            "aMule registry client is required.",
        );
    }

    if (!contractAddress) {
        throw new Error(
            "Registry contract address is required.",
        );
    }

    if (!resourceId) {
        throw new Error(
            "Resource ID is required.",
        );
    }

    return client.readContract({
        address: contractAddress,
        abi: REGISTRY_ABI,
        functionName: "getResource",
        args: [
            resourceId,
        ],
    });
}


export async function resourceExists(
    client,
    contractAddress,
    resourceId,
) {
    return client.readContract({
        address: contractAddress,
        abi: REGISTRY_ABI,
        functionName: "resourceExists",
        args: [
            resourceId,
        ],
    });
}


export async function getResourcesByOwner(
    client,
    contractAddress,
    owner,
) {
    return client.readContract({
        address: contractAddress,
        abi: REGISTRY_ABI,
        functionName: "getResourcesByOwner",
        args: [
            owner,
        ],
    });
}


export function createWallet(
    privateKey,
) {
    if (!privateKey) {
        throw new Error(
            "Private key is required.",
        );
    }

    const account =
        privateKeyToAccount(
            privateKey,
        );

    return createWalletClient({
        account,

        chain: ROBINHOOD_TESTNET,

        transport: http(
            ROBINHOOD_TESTNET.rpcUrls
                .default
                .http[0],
        ),
    });
}


export async function publishResource(
    walletClient,
    contractAddress,
    resourceId,
    contentHash,
    storageRef,
    contentType,
    source,
) {
    if (!walletClient) {
        throw new Error(
            "Wallet client is required.",
        );
    }

    if (!contractAddress) {
        throw new Error(
            "Registry contract address is required.",
        );
    }

    return walletClient.writeContract({
        address: contractAddress,

        abi: REGISTRY_ABI,

        functionName:
            "publishResource",

        args: [
            resourceId,
            contentHash,
            storageRef,
            contentType,
            source,
        ],
    });
}
