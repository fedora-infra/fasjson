<!DOCTYPE html>
<html lang="english">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Fedora Accounts System JSON API Documentation</title>
    <link rel="stylesheet" type="text/css" href="_static/pygments.css?v=4f649999" />
    <link rel="stylesheet" type="text/css" href="_static/alabaster.css?v=039e1c02" />
    <link rel="stylesheet" href="_static/custom.css" type="text/css" />
</head>
<body>
    <div class="document">
        <div class="documentwrapper">
            <div class="bodywrapper">
                <div class="body" role="main">
                    <section id="fedora-accounts-system-json-api-documentation">
                        <h1>Fedora Accounts System JSON API Documentation</h1>

                        <h2>Introduction</h2>
                        <p>Welcome to the comprehensive documentation for the Fedora Accounts System JSON API. This guide offers examples and detailed explanations to assist users in effectively utilizing various API endpoints.</p>

                        <h2>Before You Begin</h2>
                        <p>Before interacting with the API endpoints, ensure you have acquired and cached Kerberos tickets using the <code>kinit</code> command:</p>
                        <pre><code>$ kinit
                        </code></pre>
                        <p>Additionally, include the <code>--negotiate</code> option in all curl commands for SPNEGO authentication.</p>

                        <h3>/me/ Endpoint</h3>
                        <p>The /me/ endpoint retrieves detailed information about the connected user.</p>
                        <h4>Example Usage:</h4>
                        <pre><code>$ curl --negotiate -u : http://$(hostname)/fasjson/v1/me/
                        </code></pre>
                        <p>Response:</p>
                        <pre><code>{
                          "dn": "uid=admin,cn=users,cn=accounts,dc=$(domain)",
                          "service": "...",
                          "uri": "http://$(hostname)/fasjson/v1/users/admin/",
                          "username": "admin"
                        }
                        </code></pre>
                        <p><strong>Model:</strong> Me</p>
                        <ul>
                            <li><strong>dn (Exact Match):</strong> User's distinguished name.</li>
                            <li><strong>service (Exact Match):</strong> User's service information.</li>
                            <li><strong>uri (Exact Match):</strong> User's URI.</li>
                            <li><strong>username (Exact Match):</strong> User's username.</li>
                        </ul>
                        <p><strong>Explanation:</strong> The /me/ endpoint provides detailed information about the authenticated user, including the distinguished name, service details, URI, and username.</p>

                        <!-- Continue adding content for other endpoints -->

                        <h3>/users/ Endpoint</h3>
                        <p>The /users/ endpoint facilitates user-related operations.</p>
                        <h4>Example Usage:</h4>
                        <p>List all users:</p>
                        <pre><code>$ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/
                        </code></pre>
                        <p>Response:</p>
                        <pre><code>{
                          "result": [
                            {"username": "user1", ...},
                            {"username": "user2", ...},
                            ...
                          ]
                        }
                        </code></pre>
                        <p>Fetch information about a specific user:</p>
                        <pre><code>$ curl --negotiate -u : http://$(hostname)/fasjson/v1/users/{username}/
                        </code></pre>
                        <p>Response:</p>
                        <pre><code>{
                          "certificates": [...],
                          "creation": "...",
                          "emails": [...],
                          "github_username": "...",
                          "gitlab_username": "...",
                          "givenname": "...",
                          ...
                        }
                        </code></pre>
                        <p><strong>Model:</strong> User</p>
                        <ul>
                            <li><strong>certificates (Exact Match):</strong> User's certificates.</li>
                            <li><strong>creation (Exact Match):</strong> User's creation timestamp.</li>
                            <li><strong>emails (Substring Match):</strong> User's email addresses.</li>
                            <li><strong>github_username (Substring Match):</strong> User's GitHub username.</li>
                            <li><strong>gitlab_username (Substring Match):</strong> User's GitLab username.</li>
                            <li><strong>givenname (Substring Match):</strong> User's given name.</li>
                            <!-- Add more fields as necessary -->
                        </ul>
                        <p><strong>Explanation:</strong> The /users/ endpoint provides operations related to users, allowing you to list all users or fetch detailed information about a specific user.</p>

                        <h3>/groups/ Endpoint</h3>
                        <p>The /groups/ endpoint offers operations related to groups.</p>
                        <h4>Example Usage:</h4>
                        <p>List all groups:</p>
                        <pre><code>$ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/
                        </code></pre>
                        <p>Response:</p>
                        <pre><code>{
                          "result": [
                            {"groupname": "group1", ...},
                            {"groupname": "group2", ...},
                            ...
                          ]
                        }
                        </code></pre>
                        <p>Fetch information about a specific group:</p>
                        <pre><code>$ curl --negotiate -u : http://$(hostname)/fasjson/v1/groups/{groupname}/
                        </code></pre>
                        <p>Response:</p>
                        <pre><code>{
                          "description": "...",
                          "irc": "...",
                          "mailing_list": "...",
                          "uri": "...",
                          "url": "..."
                        }
                        </code></pre>
                        <p><strong>Model:</strong> Group</p>
                        <ul>
                            <li><strong>description (Substring Match):</strong> Group's description.</li>
                            <li><strong>irc (Exact Match):</strong> Group's IRC information.</li>
                            <li><strong>mailing_list (Substring Match):</strong> Group's mailing list.</li>
                            <li><strong>uri (Exact Match):</strong> Group's URI.</li>
                            <li><strong>url (Exact Match):</strong> Group's URL.</li>
                            <!-- Add more fields as necessary -->
                        </ul>
                        <p><strong>Explanation:</strong> The /groups/ endpoint provides operations related to groups, enabling you to list all groups or fetch detailed information about a specific group.</p>

                        <h2>Autogenerated Documentation</h2>
                        <p>Refer to the autogenerated documentation for additional details and examples.</p>

                        <h2>Field Masks</h2>
                        <p>Example using field masks:</p>
                        <pre><code>$ curl --negotiate -u : http://$(hostname)/fasjson/v1/me/?fields=dn,username
                        {"result": {"dn": "uid=admin,cn=users,cn=accounts,dc=$(domain)", "username": "admin"}}
                        </code></pre>
                    </section>
                </div>
            </div>
        </div>
        <div class="sphinxsidebar" role="navigation" aria-label="main navigation">
            <div class="sphinxsidebarwrapper">
                <h1 class="logo"><a href="#">Usage documentation</a></h1>
                <h3>Navigation</h3>
                <div class="relations">
                    <h3>Related Topics</h3>
                    <ul>
                        <li><a href="#">Documentation overview</a></li>
                    </ul>
                </div>
                <div id="searchbox" style="display: none" role="search">
                    <h3 id="searchlabel">Quick search</h3>
                    <div class="searchformwrapper">
                        <form class="search" action="search.html" method="get">
                            <input type="text" name="q" aria-labelledby="searchlabel" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"/>
                            <input type="submit" value="Go" />
                        </form>
                    </div>
                </div>
                <script>document.getElementById('searchbox').style.display = "block"</script>
            </div>
        </div>
        <div class="clearer"></div>
    </div>
    <div class="footer">
        &copy;2024, Paula.
        |
        Powered by <a href="http://sphinx-doc.org/">Sphinx 7.1.2</a>
        &amp; <a href="https://github.com/bitprophet/alabaster">Alabaster 0.7.13</a>
        |
        <a href="_sources/index.rst.txt" rel="nofollow">Page source</a>
    </div>
</body>
