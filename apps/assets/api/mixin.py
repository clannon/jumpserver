from typing import List

from assets.models import Node, Asset
from assets.pagination import AssetLimitOffsetPagination
from common.utils import lazyproperty, dict_get_any, is_uuid, get_object_or_none
from assets.utils import get_node, is_query_node_all_assets


class SerializeToTreeNodeMixin:
    permission_classes = ()

    def serialize_nodes(self, nodes: List[Node], with_asset_amount=False):
        if with_asset_amount:
            def _name(node: Node):
                return '{} ({})'.format(node.value, node.assets_amount)
        else:
            def _name(node: Node):
                return node.value
        data = [
            {
                'id': node.key,
                'name': _name(node),
                'title': _name(node),
                'pId': node.parent_key,
                'isParent': True,
                'open': node.is_org_root(),
                'meta': {
                    'node': {
                        "id": node.id,
                        "key": node.key,
                        "value": node.value,
                    },
                    'type': 'node'
                }
            }
            for node in nodes
        ]
        return data

    def get_platform(self, asset: Asset):
        default = 'file'
        icon = {'windows', 'linux'}
        platform = asset.platform_base.lower()
        if platform in icon:
            return platform
        return default

    def serialize_assets(self, assets, node_key=None):
        if node_key is None:
            get_pid = lambda asset: getattr(asset, 'parent_key', '')
        else:
            get_pid = lambda asset: node_key

        data = [
            {
                'id': str(asset.id),
                'name': asset.hostname,
                'title': asset.ip,
                'pId': get_pid(asset),
                'isParent': False,
                'open': False,
                'iconSkin': self.get_platform(asset),
                'meta': {
                    'type': 'asset',
                    'asset': {
                        'id': asset.id,
                        'hostname': asset.hostname,
                        'ip': asset.ip,
                        'protocols': asset.protocols_as_list,
                        'platform': asset.platform_base,
                    },
                }
            }
            for asset in assets
        ]
        return data


class FilterAssetByNodeMixin:
    pagination_class = AssetLimitOffsetPagination

    @lazyproperty
    def is_query_node_all_assets(self):
        return is_query_node_all_assets(self.request)

    @lazyproperty
    def node(self):
        return get_node(self.request)
