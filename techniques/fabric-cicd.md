# fabric-cicd

Deploying Fabric items from Git with the `fabric-cicd` Python library.

## What it does by itself

- References between items in the same repo are stored by Fabric Git as the item's logicalId with
  workspaceId `00000000-0000-0000-0000-000000000000`. On publish, fabric-cicd replaces the logicalId
  with the real item id in the target workspace and the zero GUID with the target workspace id
  (`_replace_logical_ids` and `_replace_workspace_ids` in its source; in the changelog since 0.1.10).
  So a dev pipeline calls the dev notebook and the prd pipeline the prd notebook without any
  parameter rule. A Variable Library full of item ids per environment is unnecessary for that.
- It does not remove items that disappeared from the repo unless you configure unpublishing. Delete
  leftovers yourself.

## What needs parameter.yml

Anything Fabric writes as a real id, host name or URL instead of a logicalId:

```yaml
find_replace:
  # Bind notebooks to the target lakehouse.
  - find_value: '\#\s*META\s+"default_lakehouse":\s*"([0-9a-fA-F-]{36})"'
    is_regex: "true"
    replace_value:
      Production: "$items.Lakehouse.<lakehouse_name>.id"
    item_type: "Notebook"
  - find_value: '\#\s*META\s+"default_lakehouse_workspace_id":\s*"([0-9a-fA-F-]{36})"'
    is_regex: "true"
    replace_value:
      Production: "$workspace.id"
    item_type: "Notebook"
  # Semantic models point to their source through a server name, not a logicalId.
  - find_value: 'expression\s+server\s*=\s*"([^"]+)"'
    is_regex: "true"
    replace_value:
      Production: $items.Warehouse.<warehouse_name>.sqlendpoint
    item_type:
      - SemanticModel

key_value_replace:
  - find_key: $.schedules[0].configuration.times[0]
    replace_value:
      Production: "03:00"
    file_path: "**/<pipeline_name>.DataPipeline/.schedules"
```

- The regex above binds every notebook to one lakehouse. If some notebooks use another default
  lakehouse, match on the specific dev GUID instead of any GUID.
- Direct Lake models on OneLake carry a URL with real workspace and item GUIDs: those need a rule too.
- References to items in another workspace are not replaced automatically; use
  `$workspace.<name>.$items.<type>.<name>.id`.
- The environment key (`Production` above) must match the environment name your pipeline passes
  exactly, and a Variable Library value set with the same name if you use one.

## Pipeline notes

- One `azure-pipelines.yml` (or GitHub workflow) with inline Python (`fabric-cicd`, `azure-identity`)
  is enough for a single dev-to-prod flow.
- The deploying service principal needs rights on the Fabric connections the items use, otherwise
  pipelines fail after deployment on missing connection permissions.
- Items deployed by a service principal are owned by it. Features that validate the owner (for
  example UDFs with Variable Library connections) can break; see microsoft-fabric.md.
