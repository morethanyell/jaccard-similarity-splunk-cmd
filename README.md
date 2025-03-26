# Jaccard Similarity Splunk Command
A custom Splunk calculates the mean Jaccard Similarity distance in all items in an MV field

## Sample Use Case
```
index=azure sourcetype=azure:aad:user
| dedup id
| eval proxy_addr = mvfilter(match('proxyAddresses{}', "(?i)smtp"))
| eval proxy_addr = mvmap(proxy_addr, replace(proxy_addr, "(?i)smtp:", ""))
| jaccard textfield="proxy_addr"
| where mvcount(proxy_addr) > 10 AND jaccard_distance_proxy_addr < 0.3
```

The SPL example above extracts the `proxyAddresses` field from the Azure Entra ID log source (`azure:aad:user`). This field is a multi-value (MV) field containing all possible SMTP email addresses associated with an Azure AD account.
The Jaccard Similarity Splunk Command calculates the average Jaccard Similarity score for all items in the field. It generates a new field named `jaccard_similarity_<field_name>`, representing the similarity score.
A score close to 1.0 indicates that the items are highly similar.
A lower score, such as 0.25, suggests that the items are dissimilar.

### Explanation
The example query retrieves Azure AD accounts that meet the following conditions:
- They have more than 10 proxy addresses.
- Their Jaccard Similarity score is below 0.3.

This effectively filters out users with a large number of diverse proxy addresses while retaining accounts where most proxy addresses are highly similar. A common application is identifying "Shared Mailboxes", which often have numerous but closely related proxy addresses, such as:

- noreply1@mycompany.com
- noreply2@mycompany.com
- noreply3@mycompany.com

By excluding such cases, this approach helps refine user analysis within your organization.

## Requirements
I purposely excluded from this repository the `splunklib` for lightweightedness purposes. You should be able to get this library from Splunk's Github repository for [Splunk Python SDK](https://github.com/splunk/splunk-sdk-python])
Just simply copy the `splunklib` directory into this app's bin directory.
