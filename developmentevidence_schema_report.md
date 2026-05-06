# GraphQL Introspection Report

Endpoint: `https://api.developmentevidence.3ieimpact.org/graphql`

## Schema Summary

- Query root: `Query`
- Mutation root: `Mutation`
- Subscription root: `None`
- Total types: `111`
- ENUM: `9`
- INPUT_OBJECT: `19`
- OBJECT: `75`
- SCALAR: `8`

## Directives

- `include`
  Description: Directs the executor to include this field or fragment only when the `if` argument is true.
  Locations: `FIELD`, `FRAGMENT_SPREAD`, `INLINE_FRAGMENT`
  Args: `if: Boolean!`
- `skip`
  Description: Directs the executor to skip this field or fragment when the `if` argument is true.
  Locations: `FIELD`, `FRAGMENT_SPREAD`, `INLINE_FRAGMENT`
  Args: `if: Boolean!`
- `deprecated`
  Description: Marks an element of a GraphQL schema as no longer supported.
  Locations: `FIELD_DEFINITION`, `ENUM_VALUE`
  Args: `reason: String` = `"No longer supported"`

## Queries

- `roles` -> `[Role!]!`
  Args: none
- `users` -> `UserPaginator`
  Args: `count: Int!`, `page: Int`
- `user` -> `User`
  Args: `id: Int!`
- `me` -> `User!`
  Args: none
- `aboutPage` -> `AboutPage`
  Args: none
- `support` -> `Support`
  Args: none
- `decisiontree` -> `DecisionTree`
  Args: none
- `advancedSearchHelpContent` -> `AdvancedSearchHelpContent`
  Args: none
- `recordList` -> `RecordList`
  Args: `name: String`
- `advancedSearch` -> `AdvancedSearchResponse`
  Args: `filter: WhereConstraints`, `data: AdvancedSearchInput!`
- `bookmarkRecords` -> `BookmarkRecordData`
  Args: `from: Int!`, `size: Int!`
- `record` -> `Record`
  Args: `id: Int!`
- `keywordSearch` -> `KeyWordSearchResponse`
  Args: `data: KeywordSearchInput!`
- `Newest` -> `[SearchResultResponse]`
  Args: none
- `Export` -> `Export`
  Args: `data: ExportSearchResultInput!`
- `Download` -> `Export`
  Args: `id: [ID]!`, `sort_by: String`, `export_type: String`
- `RisDownload` -> `Export`
  Args: `data: DownloadSearchResultInput!`
- `DownloadRecord` -> `Export`
  Args: `id: Int!`
- `popularSearches` -> `CommonFilterCount`
  Args: `size: Int!`
- `recordDetail` -> `RecordDetail`
  Args: `id: Int!`
- `recordCount` -> `RecordTypeCount`
  Args: none
- `fundedByList` -> `FundedByList`
  Args: `name: String`
- `whatsNews` -> `[WhatsNew]`
  Args: none

## Mutations

- `updateUserDetails` -> `UpdateUserDetailsResponse`
  Args: `data: UpdateUserDetailInput!`
- `signUp` -> `SignUpResult!`
  Args: `data: SignUpInput!`
- `socialLogin` -> `AuthPayload!`
  Args: `data: SocialLoginInput!`
- `deleteAccount` -> `DeleteAccountResponse`
  Args: none
- `createSaveSearch` -> `SavedSearch`
  Args: `searched_text: String`, `searched_result_count: Int!`, `type: SavedSearchType`, `search_type: SearchType`, `alert: Boolean`, `url: String!`
- `savedSearchdDelete` -> `DeleteSavedSearchResponse`
  Args: `id: [ID]!`
- `updateSavedSearch` -> `SavedSearch`
  Args: `id: ID!`, `searched_text: String`, `type: SearchType`, `url: String!`
- `enableDisableSavedSearchNotification` -> `UpdatedSearchNotificationResult`
  Args: `data: EnableDisableNotificationInput!`
- `createBookmarkRecord` -> `BookmarkRecord`
  Args: `record_id: ID!`
- `deleteBookmarkRecord` -> `DeleteBookmarkResponse`
  Args: `id: [ID]`
- `savedSearchedKeyword` -> `SavedSearchResult`
  Args: `keyword: String`
- `updateRecordPageView` -> `Record`
  Args: `id: ID!`
- `bookmarkedRecords` -> `BookmarkedRecordIDs`
  Args: none
- `SavedSearches` -> `SavedSearchPaginator`
  Args: `type: SavedSearchType!`, `count: Int!`, `page: Int`
- `login` -> `AuthPayload!`
  Args: `data: LoginInput`
- `refreshToken` -> `RefreshTokenPayload!`
  Args: `data: RefreshTokenInput`
- `logout` -> `LogoutResponse!`
  Args: none
- `forgotPassword` -> `ForgotPasswordResponse!`
  Args: `data: ForgotPasswordInput!`
- `updateForgottenPassword` -> `ForgotPasswordResponse!`
  Args: `data: NewPasswordWithCodeInput`
- `updatePassword` -> `UpdatePasswordResult!`
  Args: `data: UpdatePasswordInput!`

## Scalars

- `Boolean` (builtin)
  Description: The `Boolean` scalar type represents `true` or `false`.
- `CustomDateTime` (custom)
  Description: A datetime string with format `Y-m-d H:i:s`, e.g. `2019-07-27T22:00:00+00:0`.
- `DateTime` (custom)
  Description: A datetime string with format 'Y-m-d H:i:s', e.g. '2018-01-01 13:00:00'.
- `Float` (builtin)
  Description: The `Float` scalar type represents signed double-precision fractional
values as specified by
[IEEE 754](http://en.wikipedia.org/wiki/IEEE_floating_point). 
- `ID` (builtin)
  Description: The `ID` scalar type represents a unique identifier, often used to
refetch an object or as key for a cache. The ID type appears in a JSON
response as a String; however, it is not intended to be human-readable.
When expected as an input type, any string (such as `"4"`) or integer
(such as `4`) input value will be accepted as an ID.
- `Int` (builtin)
  Description: The `Int` scalar type represents non-fractional signed whole numeric
values. Int can represent values between -(2^31) and 2^31 - 1. 
- `Mixed` (custom)
  Description: Loose type that allows any value. Be careful when passing in large `Int` or `Float` literals,
as they may not be parsed correctly on the server side. Use `String` literals if you are
dealing with really large numbers to be on the safe side.
- `String` (builtin)
  Description: The `String` scalar type represents textual data, represented as UTF-8
character sequences. The String type is most often used by GraphQL to
represent free-form human-readable text.

## Enums

### `Operator`
- `EQ`
- `NEQ`
- `GT`
- `GTE`
- `LT`
- `LTE`
- `LIKE`
- `NOT_LIKE`

### `ProductType`
- `srr`
- `ier`
- `egm`

### `Provider`
- `FACEBOOK`

### `SavedSearchType`
- `saved`
- `recent`

### `SearchType`
- `keyword`
- `advanced_search`

### `SortBy`
- `relevance`
- `popular`
- `recent`

### `SortOrder`
- `ASC`
- `DESC`

### `__DirectiveLocation`
A Directive can be adjacent to many parts of the GraphQL language, a __DirectiveLocation describes one such possible adjacencies.

- `QUERY`
  Description: Location adjacent to a query operation.
- `MUTATION`
  Description: Location adjacent to a mutation operation.
- `SUBSCRIPTION`
  Description: Location adjacent to a subscription operation.
- `FIELD`
  Description: Location adjacent to a field.
- `FRAGMENT_DEFINITION`
  Description: Location adjacent to a fragment definition.
- `FRAGMENT_SPREAD`
  Description: Location adjacent to a fragment spread.
- `INLINE_FRAGMENT`
  Description: Location adjacent to an inline fragment.
- `SCHEMA`
  Description: Location adjacent to a schema definition.
- `SCALAR`
  Description: Location adjacent to a scalar definition.
- `OBJECT`
  Description: Location adjacent to an object type definition.
- `FIELD_DEFINITION`
  Description: Location adjacent to a field definition.
- `ARGUMENT_DEFINITION`
  Description: Location adjacent to an argument definition.
- `INTERFACE`
  Description: Location adjacent to an interface definition.
- `UNION`
  Description: Location adjacent to a union definition.
- `ENUM`
  Description: Location adjacent to an enum definition.
- `ENUM_VALUE`
  Description: Location adjacent to an enum value definition.
- `INPUT_OBJECT`
  Description: Location adjacent to an input object type definition.
- `INPUT_FIELD_DEFINITION`
  Description: Location adjacent to an input object field definition.

### `__TypeKind`
An enum describing what kind of type a given `__Type` is.

- `SCALAR`
  Description: Indicates this type is a scalar.
- `OBJECT`
  Description: Indicates this type is an object. `fields` and `interfaces` are valid fields.
- `INTERFACE`
  Description: Indicates this type is an interface. `fields` and `possibleTypes` are valid fields.
- `UNION`
  Description: Indicates this type is a union. `possibleTypes` is a valid field.
- `ENUM`
  Description: Indicates this type is an enum. `enumValues` is a valid field.
- `INPUT_OBJECT`
  Description: Indicates this type is an input object. `inputFields` is a valid field.
- `LIST`
  Description: Indicates this type is a list. `ofType` is a valid field.
- `NON_NULL`
  Description: Indicates this type is a non-null. `ofType` is a valid field.

## Input Objects

### `AdvancedSearchInput`
- `from: Int!`
- `size: Int!`
- `sort_by: SortBy`
- `initial_operator: String`
- `filters: FilterSelected`
- `query: String`

### `DownloadSearchResultInput`
- `export_type: SearchType!`
- `keyword: String`
- `initial_operator: String`
- `sort_by: SortBy`
- `filters: FilterSelected`
- `query: String`
- `size: Int!`

### `EnableDisableNotificationInput`
- `id: ID!`
- `alert: Boolean!`

### `ExportSearchResultInput`
- `export_type: SearchType!`
- `keyword: String`
- `initial_operator: String`
- `sort_by: SortBy`
- `filters: FilterSelected`
- `query: String`
- `size: Int!`

### `FilterSelected`
- `sector_name: [String]`
- `continents: [String]`
- `product_type: [ProductType]`
- `threeie_funded: [String]`
- `threeie_produced: [String]`
- `countries: [String]`
- `primary_theme: [String]`
- `equity_focus: [String]`
- `year_of_publication: [Int]`
- `equity_dimension: [String]`
- `evidence_programme: [String]`
- `fcv_status: [String]`
- `dataset_available: [String]`
- `primary_dac_codes: [String]`
- `un_sdg: [String]`
- `primary_dataset_availability: [String]`
- `pre_registration: [String]`
- `interventions: [String]`
- `outcome: [String]`
- `evaluation_method: [String]`
- `confidence_level: [String]`

### `ForgotPasswordInput`
- `email: String!`

### `KeywordSearchInput`
- `keyword: String`
- `from: Int!`
- `size: Int!`
- `sort_by: SortBy`
- `filters: FilterSelected`

### `LoginInput`
- `username: String!`
- `password: String!`
- `captchaToken: String!`

### `NewPasswordWithCodeInput`
- `email: String!`
- `token: String!`
- `password: String!`
- `password_confirmation: String!`

### `OrderByClause`
- `field: String!`
- `order: SortOrder!`

### `QueryFilter`
- `userQuery: String`
- `initialFilter: initialFilterSet`
- `optionalFilters: [optionalFiltersSet]`

### `RefreshTokenInput`
- `refresh_token: String`

### `SignUpInput`
- `email: String!`
- `first_name: String!`
- `last_name: String!`
- `password: String!`

### `SocialLoginInput`
- `provider: Provider!`
- `access_token: String!`

### `UpdatePasswordInput`
- `old_password: String`
- `password: String`

### `UpdateUserDetailInput`
- `first_name: String!`
- `last_name: String!`
- `email: String!`

### `WhereConstraints`
- `column: String`
- `operator: Operator` = `EQ`
- `value: Mixed`
- `AND: [WhereConstraints!]`
- `OR: [WhereConstraints!]`
- `NOT: [WhereConstraints!]`

### `initialFilterSet`
- `type: String`
- `value: String`

### `optionalFiltersSet`
- `logicOperator: String`
- `type: String`
- `value: String`

## Object Types

### `AboutPage`
- `id` -> `String`
  Args: none
- `evidence_hub_title` -> `String`
  Args: none
- `about_sub_heading` -> `String`
  Args: none
- `evidence_hub_content` -> `String`
  Args: none
- `about_banner_image` -> `String`
  Args: none
- `slides` -> `[Slide]`
  Args: none
- `tabs` -> `[Tab]`
  Args: none

### `AdvancedSearchHelpContent`
- `id` -> `ID`
  Args: none
- `advanced_search_help_title` -> `String`
  Args: none
- `advanced_search_help_content` -> `String`
  Args: none

### `AdvancedSearchResponse`
- `search_result` -> `[SearchResultResponse]`
  Args: none
- `total_count` -> `Int`
  Args: none
- `filters` -> `FilterCount`
  Args: none
- `selectedFilters` -> `selectedFiltersSet`
  Args: none

### `AggregateInfo`
- `key` -> `String`
  Args: none
- `doc_count` -> `Int`
  Args: none

### `AlternativeSuggestions`
- `text` -> `String`
  Args: none

### `AuthPayload`
- `access_token` -> `String!`
  Args: none
- `refresh_token` -> `String!`
  Args: none
- `expires_in` -> `Int!`
  Args: none
- `token_type` -> `String!`
  Args: none
- `user` -> `User!`
  Args: none

### `AuthorsSet`
- `author` -> `String`
  Args: none
- `institutions` -> `[InstitutionsSet]`
  Args: none

### `BookmarkDetails`
- `id` -> `ID`
  Args: none
- `record_id` -> `ID`
  Args: none
- `title` -> `String`
  Args: none
- `type` -> `String`
  Args: none
- `author` -> `String`
  Args: none
- `year_of_publication` -> `Int`
  Args: none
- `sector_name` -> `String`
  Args: none
- `journal` -> `String`
  Args: none

### `BookmarkRecord`
- `id` -> `ID!`
  Args: none
- `createdBy` -> `User!`
  Args: none
- `records` -> `Record!`
  Args: none
- `created_at` -> `DateTime`
  Args: none
- `updated_at` -> `DateTime`
  Args: none

### `BookmarkRecordData`
- `data` -> `[RecordDetail]`
  Args: none
- `total` -> `Int`
  Args: none

### `BookmarkedRecordIDs`
- `id` -> `[ID]`
  Args: none

### `CommonFilterCount`
- `buckets` -> `[AggregateInfo]`
  Args: none

### `ContinentsSet`
- `continent` -> `String`
  Args: none
- `countries` -> `[CountriesSet]`
  Args: none

### `CountriesSet`
- `country` -> `String`
  Args: none
- `income_level` -> `String`
  Args: none
- `fcv_status` -> `String`
  Args: none

### `DecisionTree`
- `id` -> `String`
  Args: none
- `decision_tree_title` -> `String`
  Args: none
- `decision_tree_content` -> `String`
  Args: none

### `DeleteAccountResponse`
- `status` -> `String!`
  Args: none
- `message` -> `String!`
  Args: none

### `DeleteBookmarkResponse`
- `status` -> `String!`
  Args: none
- `message` -> `String!`
  Args: none

### `DeleteSavedSearchResponse`
- `status` -> `String!`
  Args: none
- `message` -> `String!`
  Args: none

### `Export`
- `url` -> `String`
  Args: none

### `FilterCount`
- `sector_wise_count` -> `SectorDetailCount`
  Args: none
- `continents_wise_count` -> `CommonFilterCount`
  Args: none
- `product_type_wise_count` -> `ProductDetailCount`
  Args: none
- `threeie_produced_wise_count` -> `CommonFilterCount`
  Args: none
- `threeie_funded_wise_count` -> `CommonFilterCount`
  Args: none
- `countries_wise_count` -> `CommonFilterCount`
  Args: none
- `equity_focus_wise_count` -> `CommonFilterCount`
  Args: none
- `equity_dimension_wise_count` -> `CommonFilterCount`
  Args: none
- `year_of_publication_wise_count` -> `CommonFilterCount`
  Args: none
- `themes_wise_count` -> `ThemesDetailCount`
  Args: none
- `keywords_wise_count` -> `CommonFilterCount`
  Args: none
- `evidence_programme_wise_count` -> `CommonFilterCount`
  Args: none
- `fcv_wise_count` -> `CommonFilterCount`
  Args: none
- `dataset_available_wise_count` -> `CommonFilterCount`
  Args: none
- `primary_dac_codes_wise_count` -> `CommonFilterCount`
  Args: none
- `un_sdg_wise_count` -> `CommonFilterCount`
  Args: none
- `primary_dataset_availability_wise_count` -> `CommonFilterCount`
  Args: none
- `pre_registration_wise_count` -> `CommonFilterCount`
  Args: none
- `interventions_wise_count` -> `CommonFilterCount`
  Args: none
- `outcome_wise_count` -> `CommonFilterCount`
  Args: none
- `evm_wise_count` -> `CommonFilterCount`
  Args: none
- `confidence_level_wise_count` -> `CommonFilterCount`
  Args: none

### `ForgotPasswordResponse`
- `status` -> `String!`
  Args: none
- `message` -> `String`
  Args: none
- `tokens` -> `RefreshTokenPayload`
  Args: none
- `user` -> `User`
  Args: none

### `FundedBy`
- `threeie_funding` -> `Int`
  Args: none
- `other_funding_sources` -> `Int`
  Args: none

### `FundedByList`
- `funded_by_list` -> `[FundedByResponse]`
  Args: none

### `FundedByResponse`
- `id` -> `Int`
  Args: none
- `value` -> `String`
  Args: none

### `FundingAgenciesSet`
- `program_funding_agency` -> `String`
  Args: none
- `agency_name` -> `String`
  Args: none

### `ImplementationAgenciesSet`
- `implementation_agency` -> `String`
  Args: none
- `implement_agency` -> `String`
  Args: none

### `InstitutionsSet`
- `author_affiliation` -> `String`
  Args: none
- `department` -> `[String]`
  Args: none
- `author_country` -> `String`
  Args: none

### `KeyWordSearchResponse`
- `search_result` -> `[SearchResultResponse]`
  Args: none
- `total_count` -> `Int`
  Args: none
- `filters` -> `FilterCount`
  Args: none
- `selectedFilters` -> `selectedFiltersSet`
  Args: none
- `alternative_suggestions` -> `[AlternativeSuggestions]`
  Args: none

### `LogoutResponse`
- `status` -> `String!`
  Args: none
- `message` -> `String`
  Args: none

### `PageInfo`
- `hasNextPage` -> `Boolean!`
  Args: none
  Description: When paginating forwards, are there more items?
- `hasPreviousPage` -> `Boolean!`
  Args: none
  Description: When paginating backwards, are there more items?
- `startCursor` -> `String`
  Args: none
  Description: When paginating backwards, the cursor to continue.
- `endCursor` -> `String`
  Args: none
  Description: When paginating forwards, the cursor to continue.
- `total` -> `Int`
  Args: none
  Description: Total number of node in connection.
- `count` -> `Int`
  Args: none
  Description: Count of nodes in current request.
- `currentPage` -> `Int`
  Args: none
  Description: Current page of request.
- `lastPage` -> `Int`
  Args: none
  Description: Last page in connection.

### `PaginatorInfo`
- `count` -> `Int!`
  Args: none
  Description: Total count of available items in the page.
- `currentPage` -> `Int!`
  Args: none
  Description: Current pagination page.
- `firstItem` -> `Int`
  Args: none
  Description: Index of first item in the current page.
- `hasMorePages` -> `Boolean!`
  Args: none
  Description: If collection has more pages.
- `lastItem` -> `Int`
  Args: none
  Description: Index of last item in the current page.
- `lastPage` -> `Int!`
  Args: none
  Description: Last page number of the collection.
- `perPage` -> `Int!`
  Args: none
  Description: Number of items per page in the collection.
- `total` -> `Int!`
  Args: none
  Description: Total items available in the collection.

### `Permission`
- `id` -> `ID!`
  Args: none
- `name` -> `String!`
  Args: none

### `ProductAggregateInfo`
- `key` -> `String`
  Args: none
- `doc_count` -> `Int`
  Args: none
- `by_secondary_product` -> `CommonFilterCount`
  Args: none

### `ProductDetailCount`
- `buckets` -> `[ProductAggregateInfo]`
  Args: none

### `Record`
- `id` -> `ID!`
  Args: none
- `page_view` -> `Int`
  Args: none
- `createdBy` -> `User`
  Args: none
- `assignedTo` -> `User`
  Args: none
- `type` -> `String`
  Args: none
- `threeie_funded` -> `Boolean`
  Args: none
- `threeie_produced` -> `Boolean`
  Args: none
- `status` -> `String!`
  Args: none
- `archived_at` -> `DateTime`
  Args: none
- `created_at` -> `DateTime`
  Args: none
- `published_at` -> `DateTime`
  Args: none
- `attributes` -> `String`
  Args: none

### `RecordDetail`
- `product_type` -> `String`
  Args: none
- `title` -> `String`
  Args: none
- `synopsis` -> `String`
  Args: none
- `id` -> `ID`
  Args: none
- `page_view` -> `Int`
  Args: none
- `short_title` -> `String`
  Args: none
- `language` -> `[String]`
  Args: none
- `sector_name` -> `String`
  Args: none
- `journal` -> `String`
  Args: none
- `journal_volume` -> `String`
  Args: none
- `journal_issue` -> `String`
  Args: none
- `year_of_publication` -> `String`
  Args: none
- `publication_type` -> `String`
  Args: none
- `pages` -> `String`
  Args: none
- `evaluation_design` -> `String`
  Args: none
- `authors` -> `[AuthorsSet]`
  Args: none
- `continent` -> `[ContinentsSet]`
  Args: none
- `project_name` -> `[projectNameSet]`
  Args: none
- `publisher_location` -> `String`
  Args: none
- `publication_url` -> `String`
  Args: none
- `egm_url` -> `String`
  Args: none
- `report_url` -> `String`
  Args: none
- `provide_an_overall_of_the_assessment_use_consistent_style_and_wording` -> `String`
  Args: none
- `status` -> `String`
  Args: none
- `created_at` -> `DateTime`
  Args: none
- `updated_at` -> `DateTime`
  Args: none
- `assigned_to` -> `User`
  Args: none
- `created_by` -> `User`
  Args: none
- `threeie_funded` -> `String`
  Args: none
- `threeie_produced` -> `String`
  Args: none
- `is_bookmark` -> `String`
  Args: none
- `based_on_the_above_assessments_of_the_methods_how_would_you_rate_the_reliability_of_the_review` -> `String`
  Args: none
- `abstract` -> `String`
  Args: none
- `open_access` -> `String`
  Args: none
- `doi` -> `String`
  Args: none
- `equity_focus` -> `[String]`
  Args: none
- `equity_dimension` -> `[String]`
  Args: none
- `equity_description` -> `String`
  Args: none
- `keywords` -> `[String]`
  Args: none
- `evaluation_method` -> `String`
  Args: none
- `additional_method` -> `String`
  Args: none
- `additional_method_2` -> `String`
  Args: none
- `mixed_methods` -> `String`
  Args: none
- `unit_of_observation` -> `[String]`
  Args: none
- `methodology` -> `String`
  Args: none
- `main_findings` -> `String`
  Args: none
- `background` -> `String`
  Args: none
- `objectives` -> `String`
  Args: none
- `region` -> `[String]`
  Args: none
- `stateprovince_name` -> `[String]`
  Args: none
- `district_name` -> `[String]`
  Args: none
- `citytown_name` -> `[String]`
  Args: none
- `location_name` -> `[String]`
  Args: none
- `additional_url` -> `[Urls]`
  Args: none
- `grantholding_institution` -> `String`
  Args: none
- `context` -> `String`
  Args: none
- `research_questions` -> `String`
  Args: none
- `main_finding` -> `String`
  Args: none
- `policy_examples` -> `String`
  Args: none
- `headline_findings` -> `String`
  Args: none
- `evidence_findings` -> `String`
  Args: none
- `policy_findings` -> `String`
  Args: none
- `research_findings` -> `String`
  Args: none
- `review_type` -> `String`
  Args: none
- `quantitative_method` -> `String`
  Args: none
- `qualitative_method` -> `String`
  Args: none
- `overall_of_studies` -> `String`
  Args: none
- `overall_of_high_quality_studies` -> `String`
  Args: none
- `overall_of_medium_quality_studies` -> `String`
  Args: none
- `relatedArticles` -> `[RelatedArticles]`
  Args: none
- `research_funding_agency` -> `[ResearchFundingAgenciesSet]`
  Args: none
- `study_status` -> `String`
  Args: none
- `sub_sector` -> `[String]`
  Args: none
- `themes` -> `[ThemesSet]`
  Args: none
- `detail_page_url` -> `String`
  Args: none
- `methodology_summary` -> `String`
  Args: none
- `other_resources` -> `String`
  Args: none
- `impact_evaluations` -> `String`
  Args: none
- `systematic_reviews` -> `String`
  Args: none
- `dataset_available` -> `String`
  Args: none
- `dataset_url` -> `String`
  Args: none
- `evidence_programme` -> `String`
  Args: none
- `instances_of_evidence_use` -> `String`
  Args: none
- `primary_dac_code` -> `String`
  Args: none
- `secondary_dac_code` -> `String`
  Args: none
- `crs_voluntary_dac_code` -> `String`
  Args: none
- `un_sustainable_development_goal` -> `[String]`
  Args: none
- `primary_dataset_url` -> `String`
  Args: none
- `pre_registration_url` -> `String`
  Args: none
- `primary_dataset_availability` -> `String`
  Args: none
- `primary_dataset_format` -> `[String]`
  Args: none
- `secondary_dataset_name` -> `String`
  Args: none
- `secondary_dataset_disclosure` -> `String`
  Args: none
- `additional_dataset_info` -> `String`
  Args: none
- `analysis_code_availability` -> `String`
  Args: none
- `analysis_code_format` -> `[String]`
  Args: none
- `study_materials_availability` -> `[String]`
  Args: none
- `study_materials_list` -> `[String]`
  Args: none
- `pre_registration` -> `String`
  Args: none
- `protocol_pre_analysis_plan` -> `String`
  Args: none
- `ethics_approval` -> `String`
  Args: none
- `interventions` -> `[String]`
  Args: none
- `outcome` -> `[String]`
  Args: none

### `RecordList`
- `id` -> `ID`
  Args: none
- `name` -> `String`
  Args: none
- `values` -> `[RecordListValue]`
  Args: none

### `RecordListValue`
- `id` -> `ID`
  Args: none
- `list_id` -> `ID`
  Args: none
- `value` -> `String`
  Args: none

### `RecordTypeCount`
- `srr` -> `Int`
  Args: none
- `ier` -> `Int`
  Args: none
- `egm` -> `Int`
  Args: none

### `RefreshTokenPayload`
- `access_token` -> `String!`
  Args: none
- `refresh_token` -> `String!`
  Args: none
- `expires_in` -> `Int!`
  Args: none
- `token_type` -> `String!`
  Args: none

### `RelatedArticles`
- `product_type` -> `String`
  Args: none
- `product_id` -> `ID`
  Args: none
- `title` -> `String`
  Args: none

### `ResearchFundingAgenciesSet`
- `research_funding_agency` -> `String`
  Args: none
- `agency_name` -> `String`
  Args: none

### `Role`
- `id` -> `ID!`
  Args: none
- `name` -> `String!`
  Args: none
- `permissions` -> `[Permission]`
  Args: none

### `SavedSearch`
- `id` -> `ID!`
  Args: none
- `createdBy` -> `User!`
  Args: none
- `searched_text` -> `String`
  Args: none
- `searched_result_count` -> `Int!`
  Args: none
- `alert` -> `Boolean!`
  Args: none
- `type` -> `SavedSearchType!`
  Args: none
- `search_type` -> `SearchType`
  Args: none
- `url` -> `String`
  Args: none
- `created_at` -> `DateTime`
  Args: none
- `updated_at` -> `DateTime`
  Args: none
- `deleted_at` -> `DateTime`
  Args: none

### `SavedSearchPaginator`
- `paginatorInfo` -> `PaginatorInfo!`
  Args: none
- `data` -> `[SavedSearch!]!`
  Args: none

### `SavedSearchResult`
- `status` -> `String`
  Args: none

### `SearchResultResponse`
- `product_type` -> `String`
  Args: none
- `title` -> `String`
  Args: none
- `synopsis` -> `String`
  Args: none
- `id` -> `ID`
  Args: none
- `page_view` -> `Int`
  Args: none
- `short_title` -> `String`
  Args: none
- `language` -> `[String]`
  Args: none
- `sector_name` -> `String`
  Args: none
- `journal` -> `String`
  Args: none
- `journal_volume` -> `String`
  Args: none
- `journal_issue` -> `String`
  Args: none
- `year_of_publication` -> `String`
  Args: none
- `pages` -> `String`
  Args: none
- `evaluation_design` -> `String`
  Args: none
- `authors` -> `[AuthorsSet]`
  Args: none
- `continent` -> `[ContinentsSet]`
  Args: none
- `project_name` -> `[projectNameSet]`
  Args: none
- `publisher_location` -> `String`
  Args: none
- `status` -> `String`
  Args: none
- `created_at` -> `CustomDateTime`
  Args: none
- `updated_at` -> `CustomDateTime`
  Args: none
- `publication_type` -> `String`
  Args: none
- `publication_url` -> `String`
  Args: none
- `provide_an_overall_of_the_assessment_use_consistent_style_and_wording` -> `String`
  Args: none
- `assigned_to` -> `User`
  Args: none
- `created_by` -> `User`
  Args: none
- `threeie_funded` -> `String`
  Args: none
- `threeie_produced` -> `String`
  Args: none
- `is_bookmark` -> `String`
  Args: none
- `based_on_the_above_assessments_of_the_methods_how_would_you_rate_the_reliability_of_the_review` -> `String`
  Args: none
- `abstract` -> `String`
  Args: none
- `open_access` -> `String`
  Args: none
- `doi` -> `String`
  Args: none
- `equity_focus` -> `[String]`
  Args: none
- `equity_dimension` -> `[String]`
  Args: none
- `equity_description` -> `String`
  Args: none
- `keywords` -> `[String]`
  Args: none
- `evaluation_method` -> `String`
  Args: none
- `mixed_methods` -> `String`
  Args: none
- `unit_of_observation` -> `[String]`
  Args: none
- `methodology` -> `String`
  Args: none
- `main_findings` -> `String`
  Args: none
- `background` -> `String`
  Args: none
- `objectives` -> `String`
  Args: none
- `region` -> `[String]`
  Args: none
- `stateprovince_name` -> `[String]`
  Args: none
- `district_name` -> `[String]`
  Args: none
- `citytown_name` -> `[String]`
  Args: none
- `location_name` -> `[String]`
  Args: none
- `additional_url` -> `[Urls]`
  Args: none
- `grantholding_institution` -> `String`
  Args: none
- `context` -> `String`
  Args: none
- `research_questions` -> `String`
  Args: none
- `main_finding` -> `String`
  Args: none
- `policy_examples` -> `String`
  Args: none
- `headline_findings` -> `String`
  Args: none
- `review_type` -> `String`
  Args: none
- `quantitative_method` -> `String`
  Args: none
- `qualitative_method` -> `String`
  Args: none
- `overall_of_studies` -> `String`
  Args: none
- `overall_of_high_quality_studies` -> `String`
  Args: none
- `overall_of_medium_quality_studies` -> `String`
  Args: none
- `research_funding_agency` -> `[ResearchFundingAgenciesSet]`
  Args: none
- `study_status` -> `String`
  Args: none
- `sub_sector` -> `[String]`
  Args: none
- `themes` -> `[ThemesSet]`
  Args: none
- `detail_page_url` -> `String`
  Args: none
- `methodology_summary` -> `String`
  Args: none
- `other_resources` -> `String`
  Args: none
- `impact_evaluations` -> `String`
  Args: none
- `systematic_reviews` -> `String`
  Args: none
- `dataset_available` -> `String`
  Args: none
- `dataset_url` -> `String`
  Args: none
- `evidence_programme` -> `String`
  Args: none
- `instances_of_evidence_use` -> `String`
  Args: none

### `SectorAggregateInfo`
- `key` -> `String`
  Args: none
- `doc_count` -> `Int`
  Args: none
- `by_secondary_sector` -> `CommonFilterCount`
  Args: none

### `SectorDetailCount`
- `buckets` -> `[SectorAggregateInfo]`
  Args: none

### `SignUpResult`
- `status` -> `String!`
  Args: none
- `message` -> `String!`
  Args: none
- `tokens` -> `RefreshTokenPayload!`
  Args: none
- `user` -> `User!`
  Args: none

### `Slide`
- `id` -> `String`
  Args: none
- `slide_title` -> `String`
  Args: none
- `slide_content` -> `String`
  Args: none
- `slide_image` -> `String`
  Args: none

### `Support`
- `id` -> `String`
  Args: none
- `support_title` -> `String`
  Args: none
- `support_content` -> `String`
  Args: none

### `Tab`
- `id` -> `String`
  Args: none
- `tab_title` -> `String`
  Args: none
- `tab_sub_heading` -> `String`
  Args: none
- `tab_content` -> `String`
  Args: none
- `tab_image` -> `String`
  Args: none
- `order` -> `Int`
  Args: none

### `ThemesAggregateInfo`
- `key` -> `String`
  Args: none
- `doc_count` -> `Int`
  Args: none
- `by_secondary_theme` -> `CommonFilterCount`
  Args: none

### `ThemesDetailCount`
- `by_primary_theme` -> `ThemesFilterCount`
  Args: none

### `ThemesFilterCount`
- `buckets` -> `[ThemesAggregateInfo]`
  Args: none

### `ThemesSet`
- `primary_theme` -> `String`
  Args: none
- `sub_primary_theme` -> `String`
  Args: none
- `theme_type` -> `String`
  Args: none

### `UpdatePasswordResult`
- `status` -> `String!`
  Args: none
- `message` -> `String`
  Args: none

### `UpdateUserDetailsResponse`
- `message` -> `String!`
  Args: none
- `user` -> `User!`
  Args: none

### `UpdatedSearchNotificationResult`
- `message` -> `String!`
  Args: none
- `data` -> `SavedSearch!`
  Args: none

### `Urls`
- `additional_url` -> `String`
  Args: none
- `additional_url_address` -> `String`
  Args: none

### `User`
- `id` -> `ID!`
  Args: none
- `first_name` -> `String!`
  Args: none
- `last_name` -> `String!`
  Args: none
- `email` -> `String!`
  Args: none
- `roles` -> `[Role]`
  Args: none
- `permissions` -> `[Permission]`
  Args: none

### `UserPaginator`
- `paginatorInfo` -> `PaginatorInfo!`
  Args: none
- `data` -> `[User!]!`
  Args: none

### `WhatsNew`
- `id` -> `String`
  Args: none
- `whats_new_title` -> `String`
  Args: none
- `whats_new_content` -> `String`
  Args: none
- `whats_new_date` -> `String`
  Args: none
- `animation_status` -> `String!`
  Args: none

### `projectNameSet`
- `project_name` -> `String`
  Args: none
- `implementation_agencies` -> `[ImplementationAgenciesSet]`
  Args: none
- `funding_agencies` -> `[FundingAgenciesSet]`
  Args: none
- `research_funding_agencies` -> `[ResearchFundingAgenciesSet]`
  Args: none

### `selectedFiltersSet`
- `sector_name` -> `[String]`
  Args: none
- `continents` -> `[String]`
  Args: none
- `product_type` -> `[ProductType]`
  Args: none
- `threeie_funded` -> `[String]`
  Args: none
- `threeie_produced` -> `[String]`
  Args: none
- `countries` -> `[String]`
  Args: none
- `primary_theme` -> `[String]`
  Args: none
- `equity_focus` -> `[String]`
  Args: none
- `year_of_publication` -> `[Int]`
  Args: none
- `equity_dimension` -> `[String]`
  Args: none
- `fcv_status` -> `[String]`
  Args: none
- `dataset_available` -> `[String]`
  Args: none
- `primary_dac_codes` -> `[String]`
  Args: none
- `un_sdg` -> `[String]`
  Args: none
- `primary_dataset_availability` -> `[String]`
  Args: none
- `pre_registration` -> `[String]`
  Args: none
- `interventions` -> `[String]`
  Args: none
- `outcome` -> `[String]`
  Args: none
- `evaluation_method` -> `[String]`
  Args: none
- `confidence_level` -> `[String]`
  Args: none

### `verifyPasswordResult`
- `status` -> `String!`
  Args: none
- `message` -> `String!`
  Args: none
