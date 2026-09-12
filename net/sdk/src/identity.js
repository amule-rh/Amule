/**
 * aMule Net — Resource Identity
 *
 * Resource identity specification v1.
 *
 * Canonical rule:
 *
 *     raw content
 *          ↓
 *        SHA-256
 *          ↓
 *      contentHash
 *          ↓
 *       resourceId
 *
 * In v1:
 *
 *     resourceId == contentHash
 *
 * This allows identical content published by
 * different operators to remain independently
 * attributable while sharing the same content identity.
 */

import {
    keccak256,
    stringToHex,
    toBytes,
} from "viem";


/**
 * Calculate SHA-256 from UTF-8 text.
 *
 * Returns a hexadecimal hash without 0x.
 */
export async function sha256String(
    value,
) {
    if (
        typeof value !== "string"
    ) {
        throw new Error(
            "Value must be a string.",
        );
    }

    const data =
        new TextEncoder().encode(
            value,
        );

    const hash =
        await crypto.subtle.digest(
            "SHA-256",
            data,
        );

    return Array.from(
        new Uint8Array(hash),
    )
        .map(
            (byte) =>
                byte
                    .toString(16)
                    .padStart(2, "0"),
        )
        .join("");
}


/**
 * Calculate the SHA-256 content hash.
 */
export async function calculateContentHash(
    content,
) {
    if (
        typeof content !== "string"
    ) {
        throw new Error(
            "Content must be a string.",
        );
    }

    return sha256String(
        content,
    );
}


/**
 * Convert a hexadecimal hash into bytes32.
 */
export function hashToBytes32(
    hash,
) {
    if (
        typeof hash !== "string"
    ) {
        throw new Error(
            "Hash must be a string.",
        );
    }

    const normalized =
        hash.startsWith("0x")
            ? hash.slice(2)
            : hash;

    if (
        normalized.length !== 64
    ) {
        throw new Error(
            "Hash must contain exactly 32 bytes.",
        );
    }

    if (
        !/^[0-9a-fA-F]{64}$/.test(
            normalized,
        )
    ) {
        throw new Error(
            "Hash contains invalid hexadecimal characters.",
        );
    }

    return `0x${normalized}`;
}


/**
 * Create an aMule Resource ID.
 *
 * Protocol v1:
 *
 *     Resource ID = SHA-256(content)
 */
export async function createResourceId(
    content,
) {
    const hash =
        await calculateContentHash(
            content,
        );

    return hashToBytes32(
        hash,
    );
}


/**
 * Generate a deterministic protocol identifier.
 *
 * Used for namespaces and future protocol metadata.
 */
export function deterministicId(
    value,
) {
    if (
        typeof value !== "string"
    ) {
        throw new Error(
            "Value must be a string.",
        );
    }

    return keccak256(
        stringToHex(
            value,
        ),
    );
}


/**
 * Validate an aMule Resource ID.
 */
export function isValidResourceId(
    resourceId,
) {
    return (
        typeof resourceId === "string"
        &&
        /^0x[0-9a-fA-F]{64}$/.test(
            resourceId,
        )
    );
}


/**
 * Convert a Resource ID into bytes.
 */
export function resourceIdToBytes(
    resourceId,
) {
    if (
        !isValidResourceId(
            resourceId,
        )
    ) {
        throw new Error(
            "Invalid aMule Resource ID.",
        );
    }

    return toBytes(
        resourceId,
    );
}
