/**
 * aMule — Net Integration Test
 *
 * Local validation only.
 *
 * This test does NOT:
 * - connect a wallet
 * - spend gas
 * - publish data
 * - modify Net Storage
 */

import {
    createResourceRecord,
    validateResourceRecord,
    serializeResourceRecord,
} from "./resource.js";

import {
    createStorageKey,
    getNetStorageInfo,
} from "./storage.js";


const RESOURCE_ID =
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

const OPERATOR =
    "0x0000000000000000000000000000000000000001";


console.log(
    "\n=== aMule Net Integration Test ===\n"
);


// ---------------------------------------------------------
// STORAGE KEY
// ---------------------------------------------------------

const storageKey =
    createStorageKey(
        RESOURCE_ID
    );

console.log(
    "Storage key:",
    storageKey
);


// ---------------------------------------------------------
// RESOURCE RECORD
// ---------------------------------------------------------

const resource =
    createResourceRecord({
        resourceId: RESOURCE_ID,
        operator: OPERATOR,
        storageKey,
        filename: "test-resource.txt",
        contentType: "text/plain",
        size: 25,
        encrypted: true,
    });


// ---------------------------------------------------------
// VALIDATION
// ---------------------------------------------------------

if (
    !validateResourceRecord(
        resource
    )
) {
    throw new Error(
        "Resource validation failed."
    );
}

console.log(
    "Resource validation: OK"
);


// ---------------------------------------------------------
// SERIALIZATION
// ---------------------------------------------------------

const serialized =
    serializeResourceRecord(
        resource
    );

console.log(
    "\nSerialized resource:"
);

console.log(
    serialized
);


// ---------------------------------------------------------
// NET INFORMATION
// ---------------------------------------------------------

console.log(
    "\nNet Storage configuration:"
);

console.log(
    getNetStorageInfo()
);


// ---------------------------------------------------------
// SUCCESS
// ---------------------------------------------------------

console.log(
    "\n================================"
);

console.log(
    "aMule Net integration test: OK"
);

console.log(
    "No blockchain transaction was sent."
);

console.log(
    "================================\n"
);
