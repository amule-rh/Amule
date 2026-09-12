/**
 * aMule Net — Resource Identity
 *
 * Resource Identity Specification v1
 *
 * aMule separates:
 *
 *   resourceId
 *       ↓
 *   Stable logical identity
 *
 *   contentHash
 *       ↓
 *   SHA-256 fingerprint of the exact content
 *
 * This allows a resource to have multiple versions:
 *
 *   resourceId = remains stable
 *   contentHash = changes with every new content version
 *
 * The same content may also exist under different resourceIds.
 */

import {
    keccak256,
    stringToHex,
    toBytes,
} from "viem";


/**
 * Calculate SHA-256 from UTF-8 text.
 *
 * Returns hexadecimal without 0x.
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
 * Calculate SHA-256 from binary data.
 *
 * Accepts:
 * - Uint8Array
 * - ArrayBuffer
 */
export async function sha256Bytes(
    data,
) {
    if (
        data instanceof ArrayBuffer
    ) {
        data = new Uint8Array(data);
    }

    if (
        !(data instanceof Uint8Array)
    ) {
        throw new Error(
            "Data must be Uint8Array or ArrayBuffer.",
        );
    }

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
 * Calculate the content hash of a text resource.
 *
 * Content hash is always based on the actual content,
 * not metadata such as title, filename or source.
 */
export async function calculateContentHash(
    content,
) {
    return sha256String(
        content,
    );
}


/**
 * Calculate the content hash of binary data.
 */
export async function calculateBinaryContentHash(
    data,
) {
    return sha256Bytes(
        data,
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
 * Create a stable resource ID from a namespace
 * and an external stable identifier.
 *
 * Example:
 *
 * namespace:
 *     rss:https://example.com/feed.xml
 *
 * stableId:
 *     article-guid-123
 *
 * The resulting ID remains stable as long as
 * namespace + stableId remain unchanged.
 */
export async function createDeterministicResourceId(
    namespace,
    stableId,
) {
    if (
        typeof namespace !== "string" ||
        !namespace.trim()
    ) {
        throw new Error(
            "Resource namespace is required.",
        );
    }

    if (
        typeof stableId !== "string" ||
        !stableId.trim()
    ) {
        throw new Error(
            "Stable resource identifier is required.",
        );
    }

    const canonical =
        [
            "amule-resource-v1",
            namespace.trim(),
            stableId.trim(),
        ].join("\n");

    const hash =
        await sha256String(
            canonical,
        );

    return hashToBytes32(
        hash,
    );
}


/**
 * Create a cryptographically random resource ID.
 *
 * Used when a resource does not have an external
 * deterministic identity, for example user-uploaded files.
 */
export function createRandomResourceId() {
    const bytes =
        new Uint8Array(32);

    crypto.getRandomValues(
        bytes,
    );

    return (
        "0x" +
        Array.from(bytes)
            .map(
                (byte) =>
                    byte
                        .toString(16)
                        .padStart(2, "0"),
            )
            .join("")
    );
}


/**
 * Generate a deterministic protocol identifier.
 *
 * Useful for namespaces, protocol metadata
 * and future registry identifiers.
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
        typeof resourceId === "string" &&
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
