import {
  createPublicClient,
  createWalletClient,
  http,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { hashToBytes32 } from "./identity.js";

export const ROBINHOOD_TESTNET = {
  id: 46630,
  name: "Robinhood Chain Testnet",
  nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
  rpcUrls: {
    default: { http: ["https://rpc.testnet.chain.robinhood.com"] },
  },
};

export const REGISTRY_ABI = [
  {
    type: "function",
    name: "publishResource",
    stateMutability: "nonpayable",
    inputs: [
      { name: "resourceId", type: "bytes32" },
      { name: "contentHash", type: "bytes32" },
      { name: "storageRef", type: "string" },
      { name: "contentType", type: "string" },
      { name: "source", type: "string" }
    ],
    outputs: []
  },
  {
    type: "function",
    name: "getResource",
    stateMutability: "view",
    inputs: [{ name: "resourceId", type: "bytes32" }],
    outputs: [{
      type: "tuple",
      components: [
        { name: "resourceId", type: "bytes32" },
        { name: "owner", type: "address" },
        { name: "contentHash", type: "bytes32" },
        { name: "storageRef", type: "string" },
        { name: "contentType", type: "string" },
        { name: "source", type: "string" },
        { name: "createdAt", type: "uint64" },
        { name: "updatedAt", type: "uint64" },
        { name: "version", type: "uint32" },
        { name: "active", type: "bool" }
      ]
    }]
  }
];

function rpcUrl() {
  return process.env.AMULE_RPC_URL ||
    "https://rpc.testnet.chain.robinhood.com";
}

export function createRegistryClient(address) {
  if (!address) throw new Error("Registry contract address is required.");

  return createPublicClient({
    chain: ROBINHOOD_TESTNET,
    transport: http(rpcUrl()),
  });
}

export function createWallet(privateKey) {
  if (!privateKey) throw new Error("Private key is required.");
  const normalized = privateKey.startsWith("0x") ? privateKey : `0x${privateKey}`;
  return privateKeyToAccount(normalized);
}

export async function publishResource({
  contractAddress,
  privateKey,
  resourceId,
  contentHash,
  storageRef,
  contentType,
  source,
}) {
  const account = createWallet(privateKey);
  const wallet = createWalletClient({
    account,
    chain: ROBINHOOD_TESTNET,
    transport: http(rpcUrl()),
  });

  return wallet.writeContract({
    address: contractAddress,
    abi: REGISTRY_ABI,
    functionName: "publishResource",
    args: [
      hashToBytes32(resourceId),
      hashToBytes32(contentHash),
      storageRef,
      contentType || "application/octet-stream",
      source || "",
    ],
  });
}
