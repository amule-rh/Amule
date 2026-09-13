/**
 * Native aMule discovery model.
 *
 * Discovery is registry-first: resources may belong to any operator.
 * This module intentionally does not assume the operator is the local wallet.
 */

export function createDiscoveryQuery({
  query = null,
  contentType = null,
  source = null,
  operator = null,
  activeOnly = true,
} = {}) {
  return {
    protocol: "amule",
    query,
    contentType,
    source,
    operator,
    activeOnly,
  };
}

export function canRetrieveResource(resource) {
  return Boolean(
    resource &&
    resource.resourceId &&
    resource.storage &&
    resource.storage.operator &&
    resource.storage.ref
  );
}
