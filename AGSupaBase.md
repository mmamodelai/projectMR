Supabase API & Database Guide for Cursor Agents
Introduction to Supabase and Cursor Integration

Supabase is an open-source backend-as-a-service built on top of PostgreSQL. It provides a hosted Postgres database along with integrated tools for authentication, storage (file hosting), and real-time subscriptions, aiming to recreate many of Firebase’s features using open source technologies
github.com
. In practice, a Supabase "project" gives you a dedicated Postgres database and auto-generated APIs on top of it. This guide will focus primarily on the database aspects of Supabase and how an agent in the Cursor environment can interact with it via the Supabase API (mainly using the JavaScript/TypeScript client library).

Supabase’s architecture centers on a PostgreSQL database, augmented by various services. A PostgREST server sits in front of the database, exposing your schema as a RESTful API, and a Realtime server listens to the database’s replication log to broadcast changes over websockets
supabase.com
supabase.com
. Additional components include an authentication service (GoTrue) and storage server, but these are beyond the scope of this database-focused guide.

Every Supabase project is associated with a unique API URL and a set of API keys. The two primary keys are the anon (public) key and the service (secret) key. In a Cursor agent context, these keys are used to authenticate API requests:

The anon key is meant for unprivileged or client-side access (it maps to the Postgres role anon by default)
supabase.com
supabase.com
. It is safe for use in front-end or untrusted environments because it cannot bypass security rules like Row Level Security.

The service key carries the service_role privileges, meaning it can bypass Row Level Security and has full access to the database tables
supabase.com
. This key should be kept secret (used server-side or by trusted agents) as it can override security policies.

Supabase Studio (the web dashboard) provides a GUI to manage your project (view tables, run queries, manage auth, etc.), and also offers utilities like the Schema Visualizer and API docs. However, a Cursor agent will typically interact with Supabase programmatically – for example, by using the Supabase JS client library to query and modify data or by sending HTTP requests to the REST endpoints. The following sections break down the core database features of Supabase and how to use them effectively via the API.

Core Database Concepts in Supabase

Supabase uses PostgreSQL under the hood, so its database features and behavior are those of Postgres. This means you have a relational database with support for schemas, SQL tables, views, indexes, functions (stored procedures), triggers, and more. Understanding these concepts is crucial for an agent manipulating the database through Supabase’s API.

Schemas, Tables, and Data Modeling

A schema in Postgres is a namespace for organizing tables and other database objects. When you create a Supabase project, it comes with a default schema called public (which is where most of your tables will reside unless you create others). By default, Supabase’s REST API is configured to expose only the public schema to clients
supabase.com
 (and some internal schemas for its own services). You can create additional schemas and tables as needed, but note that if you want to query those via the API, you must add them to the list of exposed schemas in your project’s API settings and typically enable Row Level Security on them (more on RLS below).

Tables in Supabase are regular PostgreSQL tables. You define columns with data types (integer, text, JSONB, etc.), primary keys, and foreign keys to model relationships. Supabase does not impose any special restrictions on table design – you can use all Postgres data types and constraints. For instance, you might have a table profiles and a table posts with a foreign key from posts.author_id to profiles.id. These relationships can be leveraged in API calls (Supabase can return joined data if you request related tables in a query). The Supabase Schema Visualizer tool in the dashboard can graphically display your tables and relationships, making it easier to understand your data model at a glance (especially useful for complex schemas).

Views: You can create SQL views in the database to represent computed or joined data. Supabase will treat views much like tables for reading – you can select from views via the API (if the view is in an exposed schema and you have SELECT permissions). Views are read-only by nature (unless created as updatable views with special rules). A common use-case is to create a view that joins several tables or hides certain columns; the Supabase API can then read from that view as if it were a table. Keep in mind that materialized views (which cache the results) are also supported in Postgres if needed for performance, though they won't live-update unless refreshed.

Indexes: Since we are focusing on performance through the API, remember that large tables should have proper indexes (especially on columns you filter frequently). Supabase allows you to add indexes via SQL (e.g. using the SQL editor or migrations). Proper indexing will improve query speed for the .select() queries an agent executes, but be cautious not to over-index and affect write performance.

Functions (Stored Procedures) in Supabase

In Postgres (and thus Supabase), you can write database functions (also called stored procedures). These are pieces of SQL or PL/pgSQL code that run on the server, encapsulating logic that can be reused or executed atomically. Supabase encourages using functions for complex or batch operations because you can then call these functions through the API as Remote Procedure Calls (RPC). In fact, any SQL function you create in the database can be invoked from the Supabase client or REST endpoint using an RPC call
supabase.com
.

To create a function, you typically write a SQL CREATE FUNCTION statement. For example, using the Supabase SQL editor or migrations:

-- Create a simple function that returns a greeting
CREATE OR REPLACE FUNCTION hello_world()
RETURNS text
LANGUAGE sql
AS $$
  SELECT 'Hello world';
$$;


After creating a function, Supabase’s auto-generated API will expose an RPC endpoint for it. In the JavaScript client, you would call supabase.rpc('hello_world') to execute it
supabase.com
. Functions can accept parameters as well. For instance, if you define FUNCTION echo(text VARCHAR) RETURNS text that just returns the input, you can call supabase.rpc('echo', { text: 'hi' }). Under the hood, the Supabase client will issue a POST request to the REST endpoint like /rpc/echo with a JSON body of {"text": "hi"}. The result (data or error) will contain what the function returns or any error it raised.

Why use database functions? They allow you to execute complex operations directly on the database server, which can be more efficient than multiple round-trip calls from the client. For example, if you need to insert into multiple tables and update others in one atomic action, you could write a server-side function to do it in a transaction. Then the agent can call that function via a single RPC call. Supabase functions can also be used to enforce certain business logic or data consistency rules. Keep in mind that by default, any role can execute a new function, so you may want to restrict who can call it (Supabase allows revoking execute privileges or using SECURITY DEFINER on functions to control this)
supabase.com
supabase.com
. Also note that if your function performs SELECT/UPDATE on tables with RLS, the function will run with the caller’s permissions by default (SECURITY INVOKER) – unless you declare it as SECURITY DEFINER, which then runs with the function creator’s privileges
supabase.com
supabase.com
. Use that feature cautiously; if you do use SECURITY DEFINER to bypass RLS in a function, you must set the function’s search_path within the function for safety
supabase.com
.

You can debug and log from within functions using Postgres’s RAISE statements. For example, RAISE NOTICE 'value: %', some_var; will create a log entry visible in the Supabase dashboard logs
supabase.com
supabase.com
. This is useful for a Cursor agent if a function isn’t behaving as expected – the agent can check the Database > Logs section in Supabase Studio to see any notices or errors generated by the function.

Triggers and Automated Events

A trigger in Postgres is a mechanism to automatically execute a function in response to certain table events (row inserts, updates, deletes, or even truncates). Supabase fully supports triggers because it’s just Postgres under the hood. For example, you might create a trigger that logs changes to a logs table whenever an update happens on a critical table. Triggers consist of two parts: the trigger function (a special kind of function that returns TRIGGER) and the trigger declaration that ties it to a table and event. In SQL it looks like:

CREATE FUNCTION update_salary_log()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO salary_log(employee_id, old_salary, new_salary)
  VALUES (NEW.id, OLD.salary, NEW.salary);
  RETURN NEW;
END;
$$;

CREATE TRIGGER salary_update_trigger
AFTER UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION update_salary_log();


In this example, whenever an employees row’s salary is updated, the trigger fires after the update to insert a record into salary_log. In general, triggers can fire BEFORE or AFTER an event, and either per row or per SQL statement affecting multiple rows
supabase.com
supabase.com
. They can be used for tasks like cascading changes, enforcing complex constraints, or syncing data between tables.

Note: From an API perspective, triggers execute on the database side transparently. If a Cursor agent uses supabase.from('employees').update({...}), any associated triggers will run automatically as part of that transaction. The agent just sees the final result (it wouldn’t necessarily know a trigger ran unless it checks the effects on other tables or sees a performance difference). Triggers do not directly send feedback to the API caller except through side effects (or if a trigger throws an exception, it will fail the API call).

Supabase also offers Database Webhooks, which are a special type of trigger that sends an HTTP request to an external URL when a table event occurs. Under the hood, database webhooks are implemented as triggers using the pg_net Postgres extension
supabase.com
. This means you can set up, say, a webhook to POST to an external API whenever a new row is inserted into a orders table. The Supabase dashboard provides a UI to configure these, or you can create them via SQL (they appear as triggers calling a function supabase_functions.http_request(...)). These webhooks run asynchronously (so they won’t slow down your transaction while waiting for a response)
supabase.com
supabase.com
. For instance, you might use this feature to notify a Discord channel or call an external job each time a certain event happens in the DB.

Automated scheduling is another aspect of “automated events”. Supabase enables the Postgres extension pg_cron for cron-like scheduled jobs
supabase.com
supabase.com
. With pg_cron, you can write SQL to schedule a function to run at intervals (e.g., daily maintenance tasks). A Cursor agent could use this to set up periodic routines (though enabling and configuring an extension might require superuser access which Supabase does allow for pg_cron). For example, you could schedule a cleanup function to run every night by inserting a cron job via SQL (SELECT cron.schedule('job_name', '0 3 * * *', $$ CALL cleanup_old_records(); $$);). Once set up, the database itself will execute the function on schedule without further intervention.

Between triggers, webhooks, and cron jobs, Supabase gives you powerful ways to automate behavior inside the database. Use triggers for intra-database consistency or derivations, webhooks for notifying external systems in real-time, and cron for timed batch operations. Make sure to monitor the effects of these – for instance, infinite loops (a trigger that causes an update that fires itself again) should be avoided or carefully handled.

Security: Row Level Security and Roles

Supabase’s approach to security is built on PostgreSQL’s Role system and Row Level Security (RLS) policies. By default, when you create a new table via the Supabase dashboard, Row Level Security is enabled on it
supabase.com
. RLS is a Postgres feature that, when enabled, forces all queries to adhere to certain row access policies that you define. Supabase requires RLS to be enabled on tables in exposed schemas (like public) for safety
supabase.com
. In fact, if RLS is off on a table, the Supabase API will refuse queries from the anon or authenticated roles (to prevent accidental broad exposure). This means an agent should almost always be operating with RLS in effect, unless using the service_role key which bypasses RLS.

Row Level Security policies are basically SQL WHERE clauses that the system invisibly adds to your queries
supabase.com
supabase.com
. For example, you might have a table todos with a column user_id, and you enable RLS and add a policy: “Users can view their own todos”. In SQL this could be:

create policy "Individuals can view their own todos"
on todos for select 
using ((auth.uid()) = user_id);


Here, auth.uid() is a function Supabase provides that returns the JWT user ID of the requester. So if an unauthenticated request (no user) comes in, auth.uid() is null and the policy fails, returning no rows
supabase.com
supabase.com
. If a logged-in user with id X requests, it only allows rows where user_id = X. Policies can be far more complex (and can apply to insert, update, delete operations as well, not just select).

For a Cursor agent, the key points are:

If using the anon key (no JWT), the role is anon (unauthenticated)
supabase.com
. Typically, you would create policies like “allow anon to select * from public tables that are meant to be public”, etc. By default, without a policy, anon will see nothing and cannot insert/update either.

If the agent has or obtains a JWT for a user (perhaps via Supabase Auth), then the request will use the authenticated role and auth.uid() reflects that user’s UUID
supabase.com
. You can then set up policies for authenticated users (commonly, allow the user to access only their own rows, as above).

If the agent uses the service_role key, it is not subject to RLS by default. The service role (internally service_role Postgres role) is meant for trusted backend operations and has full rights
supabase.com
. Use this role if the agent needs to bypass all row restrictions – for example, if performing an admin task like migrating data or reading all users. Never expose the service key in client-side code or logs, since it can do anything (it's equivalent to a superuser for practical purposes on your data).

Role Management: Aside from the three main roles (anon, authenticated, service_role), Supabase allows creation of custom Postgres roles. Through the Dashboard’s Role Management UI (introduced in Supabase Studio 3.0) or via SQL, you can create roles and assign privileges. For instance, you might create a read-only role for analytics and generate a separate API key (JWT) for it via a custom authentication flow. This is an advanced scenario – most agents will use the default roles. If you do create a custom role, you’d typically issue a JWT with a "role" claim to tell Supabase to use that role for the session
supabase.com
 (Supabase’s auth system can include a role claim in JWTs to switch from the default authenticated). Custom roles can also be used for direct Postgres connections with user/password if needed. The Supabase documentation on Postgres roles provides guidance on how to create roles, grant and revoke privileges (like GRANT SELECT ON table TO role_name)
supabase.com
, and even create role hierarchies if needed
supabase.com
supabase.com
.

In summary, best practices are to keep RLS enabled and define explicit policies for any table that should be accessible via the anon or authenticated roles. Always test these policies to ensure the least privilege principle (users see only what they should). For agents performing admin tasks, use the service role and be mindful that RLS will not stop you from doing anything – so double-check any deletion or updates the agent runs under service context.

Using the Supabase JavaScript/TypeScript Client (API Usage)

Interacting with the database from a Cursor agent is typically done through Supabase’s official client library (for Node/Browser), which wraps the HTTP APIs. The common steps are:

Initialize the client with your Supabase project URL and API key.

Use the client’s methods to perform queries (select, insert, update, delete) or call RPC functions.

Handle the responses (data or error objects) accordingly.

Initializing the Supabase Client

First, make sure the @supabase/supabase-js package is available in the environment. In a JavaScript context (Node or browser), you do:

import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://your-project-ref.supabase.co'
const SUPABASE_KEY = 'your-anon-or-service-key'
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)


In Cursor, the agent might have these values in environment variables for security. Once supabase is created, you can use it to interact with the database. Under the hood, this client uses the PostgREST interface for database tables and the GoTrue interface for auth (if you use supabase.auth), but as an agent focusing on DB tasks, you will mainly call supabase.from(...) and supabase.rpc(...) methods.

Querying Data (SELECT)

To read data from a table or view, use supabase.from('<table_name>').select('<columns>'). If you call .select() with no arguments, it will return all columns
supabase.com
. For example:

const { data, error } = await supabase
  .from('profiles')
  .select('*')


This would retrieve up to 1,000 rows from the profiles table by default
supabase.com
. Supabase API has a built-in limit of 1,000 rows per request by default for performance, but you can get more by using .range() for pagination or adjusting the limit in the API settings. It’s recommended to paginate if you expect more than a thousand records, to avoid large payloads
supabase.com
.

You can specify certain columns or even nested relationships in the select string. For example, if posts has a foreign key to profiles, you could do:

const { data } = await supabase
  .from('posts')
  .select('id, title, profiles(name)')


This would fetch each post’s id and title, and include the associated profile’s name (the syntax profiles(name) leverages the foreign key to join). The Supabase docs show examples of querying nested relationships and even renaming keys
supabase.com
, but be aware that each nested select may perform additional queries internally. Simpler alternative: perform the join logic in a SQL view or use RPC if things get complex.

Filtering: The supabase client provides chainable filter methods like .eq(), .neq(), .gt(), .lt(), .like(), .ilike() (case-insensitive like), .in(), .contains() (for arrays or JSON), etc. For instance:

const { data } = await supabase
  .from('posts')
  .select('*')
  .eq('author_id', someUserId)
  .like('title', '%hello%')
  .order('created_at', { ascending: false })
  .range(0, 49)


This would fetch posts by a certain author with "hello" in the title, sorted by newest first, returning the first 50 results. All these filters translate into query parameters on the REST request.

Single row: If you expect a query to return at most one row (e.g., selecting by a unique primary key), you can chain .single() at the end. This will cause the client to return a single object instead of an array. If zero or multiple rows are returned, it will throw an error. Alternatively, .maybeSingle() returns either an object or null (without treating not-found as an error). These are helpful for agents to simplify logic when querying by unique keys.

Inserting Data (INSERT)

To create a new record, use .insert(). For example:

const { data, error } = await supabase
  .from('profiles')
  .insert({ id: 'uuid-1234', name: 'Alice', created_at: new Date() })


You can insert a single object or an array of objects for batch insert. The result data will, by default, contain the inserted rows including any default or computed columns. (Supabase will append a returning=* to the SQL insert by default.) If you want to insert without getting back the data (to save bandwidth), you can pass an option { returning: 'minimal' } to .insert.

If the table has Row Level Security enabled (most do by default), make sure a policy allows the insert. Otherwise you’ll get an error like "new row violates row-level security policy for table X". For example, if using the anon role, you might need a policy like ALLOW anon INSERT WITH CHECK (...) in place. If no policy exists for the role, the insert will be forbidden.

One special insert operation is upsert – an "update or insert" if conflict. Supabase supports .upsert() which behaves like an insert, except it will update existing rows that conflict on a unique key. You need to specify a unique key (or the table’s primary key is used by default) for upsert to know how to detect conflicts. For example:

const { error } = await supabase
  .from('profiles')
  .upsert({ id: 'uuid-1234', name: 'Alice', updated_at: new Date() })


This will insert a profile if id='uuid-1234' doesn’t exist, or update the existing row with the new values if it does exist. Use upsert carefully – ensure that your payload has all necessary fields (including those that might be overwritten). Upsert is convenient for cache or replication scenarios.

Updating Data (UPDATE)

To modify existing rows, use .update() with a similar syntax to insert, and always include a filtering condition (like .eq) to target specific rows. For example:

const { data, error } = await supabase
  .from('profiles')
  .update({ name: 'Alice Wonderland' })
  .eq('id', 'uuid-1234')
  .select()


This will find the profile with id = 'uuid-1234' and set its name to "Alice Wonderland". Here we chained .select() to return the updated row(s) in data
supabase.com
. By default, the supabase API does not return the updated rows for an update operation – it returns only an error (if any) and an empty data or metadata about how many rows were modified. If you want the updated record(s) back, you must chain a .select() as shown
supabase.com
supabase.com
. This is a common point of confusion: forgetting .select() after an update will lead to data being null even if the update succeeded (but error will be null too in that case).

Also note, as with deletes (below), if you perform an update on a table with RLS, the update statement can only target rows the role is allowed to SELECT (or specifically allowed to UPDATE) via policies. If your policy doesn’t allow a user to “see” a row, they also can’t update it (the database doesn’t know it exists for them). This means an update query might silently affect 0 rows if the policy filters them out. Always ensure your RLS policies cover the roles and conditions under which updates can happen.

Deleting Data (DELETE)

Deleting rows uses .delete() with a filter to specify which rows to remove. For example:

const { data, error } = await supabase
  .from('posts')
  .delete()
  .eq('id', 42)
  .select()


This would delete the row with id = 42 from the posts table and return the deleted row’s data (because we chained .select() after the delete)
supabase.com
. By default, like updates, deleted rows are not returned unless you request them
supabase.com
. If you omit .select(), the data will likely be null, and you can check an error or the HTTP response status to confirm deletion. Chaining .select() after a delete is useful if you want to confirm what was deleted or need some fields from the deleted record.

When deleting with RLS in effect, the same principle as updates applies: the role must have permission (usually via a SELECT policy or a DELETE policy) to see those rows. If your delete query is not removing anything and not giving an error, suspect an RLS issue – e.g., "only rows visible through SELECT policies are deleted... by default no rows are visible" unless a policy allows it
supabase.com
. In practical terms, you might need to have a FOR SELECT ... USING (...) policy that matches the rows, even if you also have a FOR DELETE policy. Otherwise, the DELETE will find 0 rows (because the selection criteria under the covers found nothing visible to delete). This is a subtle detail: Supabase’s delete and update operations internally do a SELECT to identify rows (respecting RLS) before deleting/updating them
supabase.com
. Ensure your RLS policies for mutating data include a USING clause that allows the row to be seen and maybe a separate WITH CHECK for inserts/updates if necessary.

Calling Stored Procedures (RPC)

We covered creating and calling RPC functions earlier, but to reiterate the usage in the JS client: use supabase.rpc(). A couple of examples:

const { data, error } = await supabase.rpc('hello_world')


Calls a function with no parameters. And:

const { data, error } = await supabase.rpc('echo', { text: 'Hi there' })


Calls a function echo(text) with the argument. The data will contain whatever the function returns (could be a scalar, a row, or even a set of rows if the function returns a table type).

You can even apply filters after an RPC call if the function returns a set (table). For example, if you had an RPC list_stored_countries() that returns country records, you could do:

const { data } = await supabase
  .rpc('list_stored_countries')
  .eq('region', 'EU')
  .single()


In this contrived example, .eq('region', 'EU') would filter the results of that function call (assuming it returns a table with a region column), and .single() asserts that only one result should come back
supabase.com
.

One important option: if you have read replicas (Supabase supports read-only replicas for scaling reads), you might want an RPC to run on a replica. By default, all writes and function calls go to the primary. But if you have a function that is labeled as IMMUTABLE or just meant to fetch data, you can call it with { head: true } (in older client) or { get: true } in newer versions to direct it to a replica
supabase.com
supabase.com
. This is an advanced optimization which likely isn’t needed unless your app is at significant scale or you have heavy read functions.

Real-time Subscriptions (optional)

While not the main focus of this guide, it’s worth noting that Supabase’s real-time feature allows an agent to subscribe to database changes over websockets rather than polling. For example, using the JS client:

const channel = supabase
  .channel('table_changes')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' }, payload => {
      console.log('New message:', payload.new)
  })
  .subscribe()


This would invoke the callback whenever a new row is inserted into public.messages. Under the hood, Supabase’s Realtime server is listening to Postgres WAL (Write-Ahead Log) and pushing changes to subscribers
github.com
. In a Cursor agent scenario, you might use this to react to changes without continuously querying. For example, an agent could subscribe to a jobs table and wake up when a new job is inserted. Just keep in mind that maintaining a live subscription requires the environment to support long-lived connections and the agent to remain running. If the Cursor environment is ephemeral or stateless, real-time might be less applicable. But if you do use it, be sure to handle reconnections and unsubscribing (channel.unsubscribe()) to avoid resource leaks.

Supabase Tools and Best Practices for Development

This section highlights some tools provided by Supabase and recommended practices when building or debugging through the API.

Schema Visualizer and Database Design

Supabase Studio includes a Schema Visualizer that can automatically draw an ERD (entity-relationship diagram) of your database schema. This is a purely visual tool – it doesn’t affect the database – but it’s extremely useful for understanding how tables link together, especially in a collaborative environment or when the schema is large. If an agent is trying to figure out relationships (like which foreign keys exist), the visualizer can help confirm that (for example, a line between profiles.id and posts.author_id). Use this tool to double-check foreign key setups or just to communicate the schema to team members. It’s available in the Database section of the dashboard.

When designing your schema, follow normal relational design principles (normalize when appropriate, use foreign keys for integrity, add indexes on frequently queried fields). Supabase does not add any magical constraints beyond Postgres defaults – e.g., if you need a uniqueness constraint, be sure to add a unique index. The Table Editor in the dashboard can add columns or indexes for you, but those changes are essentially generating SQL ALTER TABLE commands under the hood.

A tip: consider using SQL migrations from the start to track schema changes (see Migrations below). Even though you can click around in the UI to change the schema, having those changes captured as SQL scripts is invaluable for reproducibility and for when the agent moves from a dev environment to production.

API Documentation and Reference

For every Supabase project, the API docs section (found under Settings -> API in the dashboard) auto-generates documentation for your tables, including example curl requests and the endpoints. This can be very handy for an agent to quickly see the exact REST endpoint for a given table or function. It shows the base URL (e.g. https://xyzcompany.supabase.co/rest/v1/) and then endpoints for each table (for example, GET /profiles to select, POST /profiles to insert, etc.), as well as the shape of payloads and response. It also lists your available RPC functions endpoints under a section (e.g., POST /rpc/your_function). If the agent is unsure how to formulate a query through the API, the docs here provide a template. Additionally, it lists the HTTP headers needed – notably the apikey (your anon or service key) and the Authorization: Bearer <token> if using a user JWT. The Supabase JS client handles these headers internally (using the key you provided and the auth state if any), but for manual requests it’s crucial to include them.

Supabase also has official documentation online (which we’ve cited throughout) that covers everything from usage of the client libraries to deep Postgres features. Agents should refer to these docs for specifics (for example, how to filter on JSON fields, how to use full-text search with the textsearch function, etc.). The official docs include guides as well as a full API reference for the client libraries. There’s even a graphical Playground (on supabase.com website) where you can test queries if you have a service key.

Managing Migrations and Schema Changes

In a development lifecycle, you’ll frequently need to change the database schema – add new tables, alter columns, create new functions, etc. Supabase provides a CLI tool and a migration system to help with this. The recommended practice is to write or generate SQL migration files and apply them, rather than making adhoc changes that aren’t tracked.

Supabase Migrations: When you create a Supabase project, you can use supabase CLI to pull the initial schema. The CLI can generate migration files when you make changes via the Studio, or you can manually create migration SQL files. Each migration is just SQL statements (e.g., CREATE TABLE ..., ALTER TABLE ...). In a repository, you might have a supabase/migrations/ folder with files like 0001_init.sql, 0002_add_profiles.sql, etc. You can apply these to your database with commands like supabase db push (which pushes all local migrations to the Supabase cloud)
supabase.com
.

If a Cursor agent needs to modify the schema (for example, add a column), there are a few ways to do it:

Use the Supabase CLI: by running a migration or using supabase db commands. In a programmatic context, the agent could invoke CLI commands if allowed by the environment.

Use the SQL Editor in Supabase Studio: an agent could output the SQL ALTER TABLE statement and prompt a developer to run it, or if the agent has an automated way to run SQL (some environments allow direct SQL via an admin connection), it could execute the DDL.

Use supabase-js with RPC: Note that the normal Supabase REST API does not allow arbitrary ALTER TABLE or DDL statements. It’s purely for data. To run DDL from the API side, one trick is to create a Postgres function that executes dynamic SQL (as superuser) and then call it via RPC using the service role. However, this is not generally recommended or enabled due to security (and superuser access is restricted on Supabase cloud). So, most schema changes will be done outside the standard data API.

Best practice: treat schema changes as migrations in code. This means if the agent is writing a fix or new feature, it should generate the SQL for it (possibly providing it to the user to execute in the database). This ensures consistency across environments (dev/staging/prod). Supabase’s CLI can even diff your local schema against the remote to create a migration script automatically (using supabase db diff). This could be integrated into the development workflow or CI.

Also, Supabase has recently introduced Database Branching – you can create branches (copies) of your database for testing, similar to git branches. This is useful for preview environments or for an agent to experiment in an isolated copy without affecting production data. Branching can be done via the CLI or dashboard. Under the hood, a branch is a separate Postgres instance forked from a point in time of the main database. This is an emerging feature that can be very useful to avoid accidents in production while iterating on schema or large data changes.

Debugging and Troubleshooting Tips

Even with best practices, issues will arise. Here are common problems and how to address them in a Cursor agent context:

Authentication & Permission Errors: If an API call returns an error like HTTP 401 Unauthorized or 403 Forbidden, first check that you provided the correct API key or token. In the Supabase JS client, the key is set at initialization – if it’s wrong or missing, every request will fail (often with a 401). If the key is correct and you still get Forbidden, the next likely cause is RLS. A 403 forbidden with a message about “row level security” or “no insert permission” means the row-level security policy blocked the operation. In that case, review the RLS policies on the table: does the role (anon or authenticated) have a policy allowing this action? If not, either adjust the policies or use the service key for this operation (if it’s something that should be done by a privileged agent). Keep in mind that using the service role bypasses RLS entirely, so ensure your logic is correct to avoid unintended data access or modification.

Row Level Security gotchas: As mentioned, one specific issue can be update/delete doing nothing because the role can’t see the rows. For example, if an agent tries to delete().eq('id', 5) and nothing happens (no error, data empty), it might be that RLS prevented it (the API won’t explicitly error if zero rows match – it just deletes zero rows). Supabase docs note that if you use delete with filters under RLS, only rows visible through SELECT policies are deleted
supabase.com
. The agent should verify that a SELECT policy exists that matches those rows for that role. If not, the solution is to create an appropriate policy, or perform the action with a higher-privilege role.

Syntax or Reference Errors: If you get an error like “column does not exist” or “syntax error” from an RPC or query, double-check your code. For instance, JSON field filters in supabase use -> or ->> operators in .eq() (as the docs show, you can filter on JSON fields using the column->>key syntax). If you see an error about a column in a filter, ensure you spelled it right and the casing matches (Postgres is case-sensitive unless identifiers are quoted).

Large data or performance issues: If a select query is very slow or times out (Supabase might time out queries that run too long), consider if an index is needed or if you’re requesting too much data at once. Use .limit() or .range() to page through data rather than pulling everything. Also fetch only the columns you need (explicit .select('col1, col2')) to reduce payload. If you have complex filtering that isn’t feasible via the standard query builder, you can always resort to writing a SQL function to do it server-side and call that via RPC.

Trigger and Function debugging: If your trigger isn’t working, ensure that the trigger function was created and that the trigger is attached to the correct table and event. Remember that creating a trigger requires the function to exist first. If changes aren’t happening, check if the trigger might be deferring (e.g., if declared as AFTER each statement vs each row). Also, triggers won’t fire on imports done via the copy command or certain bulk operations unless specified as each row triggers. For debugging functions (trigger or not), use RAISE NOTICE in the function and then check Supabase Logs (in Studio, under Database -> Logs) to see those notices or any errors the function threw
supabase.com
supabase.com
. Supabase logs also capture errors like constraint violations, etc., which can be invaluable to troubleshoot failed transactions that the API just reports as “500 Server error” without detail.

Supabase CLI and local development: If you are running a local Supabase instance (via supabase start), note that the API URL will be different (usually http://localhost:54321 for the REST API). Also, the anon and service_role keys differ in a local instance (they are printed in the terminal on start). An agent should ensure it’s using the correct endpoint and keys depending on environment. For example, in Cursor’s local testing, you might target the local supabase to avoid messing with prod data. Just swap the URL and key accordingly.

Connection issues: If the agent fails to reach the Supabase API (network error), check internet connectivity or whether the environment allows outgoing requests. In some sandbox settings, external requests might be blocked – Cursor usually does allow them if configured. If using the database connection string directly (less common for an agent, but possible via a Postgres client library), ensure the connection string is correct and the IP address is allowed (Supabase can require you to allow the IP or use TLS). Generally, stick to the supabase-js client which handles connectivity details.

Concurrent modifications: Supabase (Postgres) fully supports transactions and consistent reads, but if your agent code does multiple requests in a sequence, be mindful of race conditions. For example, if you do a select then an update based on it, the data might have changed in between. If this matters, consider doing the logic in a single RPC (so it’s one transaction), or using Postgres locks or at least checking rows again before finalizing changes. This isn’t Supabase-specific, just general DB practice.

Rate limits: Supabase cloud has some rate limiting (particularly on auth and maybe on some API usage to prevent abuse). If an agent is making a very large number of API calls in a short time, it could hit limits (the response might be HTTP 429 Too Many Requests). If that happens, implement exponential backoff or batching of requests. Using RPC to do more work server-side can also mitigate hitting those limits by reducing number of calls.

Resource exhaustion: If you do heavy data work, you might run into database resource limits (like CPU, memory, or connection limits). Supabase has a built-in connection pooler (Supavisor) that handles a large number of connections gracefully
supabase.com
. But an agent should still close any real-time subscriptions or open connections when done. If using the JS client, when you’re finished with it (in a long-running process), you can call supabase.removeAllSubscriptions() to clean up real-time connections, though normally they auto-close on process exit.

In case of any persistent issues, the Supabase community (Discord, forums) is very active, and the official docs have a Troubleshooting section
supabase.com
 for common problems. As an agent, always interpret error messages carefully – they often indicate exactly what’s wrong (e.g., “violates foreign key constraint” or “null value in column violates not-null constraint” tells you the data didn’t conform to the schema).

Best Practices Recap

Use Service Key for Admin Tasks: If the agent needs to perform a task that a normal user shouldn’t (like backfilling an entire table, or reading all user data for analysis), use the service_role key. This avoids RLS and permission issues. Just be very careful with what you do as service_role since nothing will stop a bad query from running. Consider writing read-only queries or safe updates in functions and calling those, to encapsulate logic.

Use RLS for Multi-user Data Security: If your application has user-specific data, enforce it with RLS policies. It’s more secure than filtering in the client, and Supabase makes it easy by integration with auth. Test policies thoroughly.

Migrate and Test in Lower Environment: Don’t apply schema changes directly to production without testing. Use a dev Supabase project or a database branch. The Supabase CLI can run a local instance which is identical to cloud for testing migrations quickly.

Leverage Database Features: Rather than coding everything in the agent, remember the database can do a lot:

Use foreign keys and on-delete cascades instead of trying to manually maintain relational integrity.

Use triggers for automatic computations (instead of the agent calculating something then storing it, let the DB trigger handle it to avoid inconsistencies).

Use stored functions for complex transactions or reuse.

Use database constraints (unique, check constraints) to enforce rules – they will throw errors that the agent can catch if something violates a rule, which is safer than silently accepting bad data.

Monitor and Log: Supabase provides Postgres logs (including errors, and even your custom RAISE NOTICE from functions). Use them to debug. You can also enable extensions like pg_stat_statements (which Supabase has available) to analyze query performance if needed. If an agent is responsible for a heavy operation, it might be wise to log how long queries took or if any slow queries event occurred. Supabase’s dashboard also shows basic query performance insights and database CPU/memory metrics.

Cleanup: If your agent creates any ephemeral database objects (temporary tables, etc.), ensure they get cleaned up. Temp tables in Postgres are per-connection and disappear when the session ends, so not usually an issue unless you hold connections open. If you create any persistent helper tables or debug tables, drop them when done to avoid cluttering the schema.

By following these guidelines and using the robust features of Supabase’s Postgres underpinnings, a Cursor agent (or developer) can interact with the database confidently and efficiently. Always refer back to official documentation for the latest updates – Supabase is actively developed, and new features (like improved role management UIs, new extensions, or updated client library methods) are regularly released. Happy building with Supabase! 
github.com
supabase.com