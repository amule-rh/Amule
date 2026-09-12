/**
 * aMule Net — Resource Identity
 *
 * Deterministic resource identity utilities.
 *
 * Rule:
 *
 *     canonical content
 *          ↓
 *        SHA-256
 *          ↓
 *      contentHash
 *          ↓
 *       resourceId
 *
 * The same content must always produce
 * the same identity.
 */

import {
    keccak256,
    stringToHex,
    toBytes,
} from "viem";


/**
 * Calculate the SHA-256 hash of a string.
 *
 * Returns a hexadecimal hash without the 0x prefix.
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
 * Calculate a deterministic hash
 * from a resource title and content.
 *
 * Canonical representation:
 *
 *     title + "\\n" + content
 */
export async function calculateContentHash(
    title,
    content,
) {
    if (
        typeof title !== "string"
    ) {
        throw new Error(
            "Title must be a string.",
        );
    }

    if (
        typeof content !== "string"
    ) {
        throw new Error(
            "Content must be a string.",
        );
    }

    const canonical =
        `${title}\n${content}`;

    return sha256String(
        canonical,
    );
}


/**
 * Convert a SHA-256 hexadecimal hash
 * into a bytes32-compatible value.
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
        !/^[0-9a-fA-F]+$/.test(
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
 * Create the aMule Resource ID.
 *
 * For now Resource ID is identical to the
 * SHA-256 content hash.
 */
export async function createResourceId(
    title,
    content,
) {
    const hash =
        await calculateContentHash(
            title,
            content,
        );

    return hashToBytes32(
        hash,
    );
}


/**
 * Generate a deterministic identifier
 * for arbitrary textual metadata.
 *
 * This is useful for future indexing,
 * namespaces and protocol-level identifiers.
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
 * Validate a Resource ID.
 */
export function isValidResourceId(
    resourceId,
) {
    if (
        typeof resourceId !== "string"
    ) {
        return false;
    }

    if (
        !/^0x[0-9a-fA-F]{64}$/.test(
            resourceId,
        )
    ) {
        return false;
    }

    return true;
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
