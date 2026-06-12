{% materialization view, adapter='hive' -%}
    {%- set identifier = model['alias'] -%}
    {%- set target_relation = api.Relation.create(
        identifier=identifier,
        schema=schema,
        database=database,
        type='view'
    ) -%}
    {% set grant_config = config.get('grants') %}

    {{ run_hooks(pre_hooks) }}

    {#
      The Hive adapter can report an "approximate match" when the metastore
      returns an existing relation with different schema casing (for example,
      BRONZE vs bronze). Dropping the view directly avoids that lookup path.
    #}
    {% call statement('drop_existing_view') -%}
        drop view if exists {{ target_relation.render() }}
    {%- endcall %}

    {% call statement('main') -%}
        {{ get_create_view_as_sql(target_relation, sql) }}
    {%- endcall %}

    {% set should_revoke = should_revoke(False, full_refresh_mode=True) %}
    {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

    {{ run_hooks(post_hooks) }}

    {{ return({'relations': [target_relation]}) }}
{%- endmaterialization %}
