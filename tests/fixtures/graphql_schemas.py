"""Fixtures with GraphQL schemas for testing."""

import pytest


@pytest.fixture(name="prev_schema_01")
def fixture_previous_schema_01():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
    }
    """


@pytest.fixture(name="new_schema_01")
def fixture_new_schema_01():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
        age: Int
        status: UserStatus
    }

    type Post {
        id: ID! @id
        title: String!
        content: String
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
        PENDING
    }
    """


@pytest.fixture(name="prev_schema_02")
def fixture_previous_schema_02():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        posts: [Post] @relation(name: "UserPosts", onDelete: CASCADE)
    }

    type Post {
        id: ID! @id
        author: User @relation(name: "UserPosts")
    }
    """


@pytest.fixture(name="new_schema_02")
def fixture_new_schema_02():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts")
        roles: [Role] @relation(name: "UserRoles", link: TABLE)
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts")
        tags: [Tag] @relation(name: "PostTags", link: TABLE)
    }

    type Role {
        id: ID! @id
        name: String! @db(rename: "role_name")
        hashtags: [String]
        users: [User] @relation(name: "UserRoles", link: TABLE)
    }

    type Tag {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "PostTags", link: TABLE)
    }
    """


@pytest.fixture(name="prev_schema_03")
def fixture_previous_schema_03():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts", onDelete: CASCADE)
        roles: [Role] @relation(name: "UserRoles", link: TABLE)
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts")
    }

    type Role {
        id: ID! @id
        name: String!
        users: [User] @relation(name: "UserRoles", link: TABLE)
    }
    """


@pytest.fixture(name="new_schema_03")
def fixture_new_schema_03():
    """Fixture with new GraphQL schema."""
    return """
    type User { id: ID! @id }

    type Post { id: ID! @id }

    type Role { id: ID! @id }
    """


@pytest.fixture(name="prev_schema_04")
def fixture_previous_schema_04():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! }

    type Profile { id: ID! @id bio: String }
    """


@pytest.fixture(name="new_schema_04")
def fixture_new_schema_04():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        profile: Profile @relation(name: "UserProfile")
    }

    type Profile {
        id: ID! @id
        bio: String
        user: User @relation(name: "UserProfile", onDelete: CASCADE)
    }
    """


@pytest.fixture(name="prev_schema_05")
def fixture_previous_schema_05():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! }
    type Profile { id: ID! @id bio: String }
    """


@pytest.fixture(name="new_schema_05")
def fixture_new_schema_05():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        profile: Profile @relation(name: "UserProfile", onDelete: CASCADE)
    }

    type Profile {
        id: ID! @id
        bio: String
        user: User @relation(name: "UserProfile")
    }
    """


@pytest.fixture(name="prev_schema_06")
def fixture_previous_schema_06():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id }
    type Profile { id: ID! @id }
    """


@pytest.fixture(name="new_schema_06")
def fixture_new_schema_06():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        profile: Profile @relation(name: "UserProfile", onDelete: SET_NULL)
    }

    type Profile {
        id: ID! @id
        bio: String
        user: User @relation(name: "UserProfile")
    }
    """


@pytest.fixture(name="prev_schema_07")
def fixture_previous_schema_07():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! }

    type Post { id: ID! @id title: String! }
    """


@pytest.fixture(name="new_schema_07")
def fixture_new_schema_07():
    """Fixture with new GraphQL schema."""
    return """
    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }

    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts")
    }
    """


@pytest.fixture(name="new_schema_07b")
def fixture_new_schema_07b():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts")
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """


@pytest.fixture(name="prev_schema_08")
def fixture_previous_schema_08():
    """Fixture with previous GraphQL schema."""
    return """
    type Category { id: ID! @id name: String! }
    """


@pytest.fixture(name="new_schema_08")
def fixture_new_schema_08():
    """Fixture with new GraphQL schema."""
    return """
    type Category {
        id: ID! @id
        name: String!
        subcategories: [Category] @relation(
            name: "CategoryHierarchy", link: TABLE, onDelete: CASCADE
        )
    }
    """


@pytest.fixture(name="prev_schema_09")
def fixture_previous_schema_09():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! }

    type Post { id: ID! @id title: String! }
    """


@pytest.fixture(name="new_schema_09")
def fixture_new_schema_09():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts", onDelete: SET_NULL)
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """


@pytest.fixture(name="prev_schema_10")
def fixture_previous_schema_10():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! email: String }
    """


@pytest.fixture(name="new_schema_10")
def fixture_new_schema_10():
    """Fixture with new GraphQL schema."""
    return """
    type User { id: ID! @id name: String! }
    """


@pytest.fixture(name="prev_schema_11")
def fixture_previous_schema_11():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! }
    """


@pytest.fixture(name="new_schema_11")
def fixture_new_schema_11():
    """Fixture with new GraphQL schema."""
    return """
    type User { id: ID! @id name: String! age: Int }
    """


@pytest.fixture(name="prev_schema_12")
def fixture_previous_schema_12():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id name: String! email: String }
    """


@pytest.fixture(name="new_schema_12")
def fixture_new_schema_12():
    """Fixture with new GraphQL schema."""
    return """
    type User { id: ID! @id name: String! email: String! }
    """


@pytest.fixture(name="prev_schema_13")
def fixture_previous_schema_13():
    """Fixture with previous GraphQL schema."""
    return """
    enum UserStatus {
        ACTIVE
        INACTIVE
    }

    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }
    """


@pytest.fixture(name="new_schema_13")
def fixture_new_schema_13():
    """Fixture with new GraphQL schema."""
    return """
    enum UserStatus {
        ACTIVE
        INACTIVE
        PENDING
    }

    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }
    """


@pytest.fixture(name="prev_schema_14")
def fixture_previous_schema_14():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
    }
    """


@pytest.fixture(name="new_schema_14")
def fixture_new_schema_14():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
    }
    """


@pytest.fixture(name="prev_schema_15")
def fixture_previous_schema_15():
    """Fixture with previous GraphQL schema."""
    return """
    enum UserStatus {
        ACTIVE
        INACTIVE
    }

    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }
    """


@pytest.fixture(name="new_schema_15")
def fixture_new_schema_15():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
    }
    """


@pytest.fixture(name="prev_schema_16")
def fixture_previous_schema_16():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
    }

    type Post {
        id: ID! @id
        title: String!
    }
    """


@pytest.fixture(name="new_schema_16")
def fixture_new_schema_16():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
    }
    """


@pytest.fixture(name="prev_schema_17")
def fixture_previous_schema_17():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
    }
    """


@pytest.fixture(name="new_schema_17")
def fixture_new_schema_17():
    """Fixture with new GraphQL schema."""
    return """
    type Employee {
        name: String! @default(value: "emp_123")
        age: Int @default(value: 18)
        email: String @unique
        status: EmployeeStatus @default(value: CONTRACTED)
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }

    enum EmployeeStatus { ACTIVE INACTIVE FIRED CONTRACTED }
    """


@pytest.fixture(name="prev_schema_18")
def fixture_previous_schema_18():
    """Fixture with previous GraphQL schema."""
    return """
    type User { id: ID! @id }
    type Role { id: ID! @id }
    """


@pytest.fixture(name="new_schema_18")
def fixture_new_schema_18():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        roles: [Role] @relation(
            name: "UserRoles", link: TABLE, onDelete: CASCADE
        )
    }

    type Role {
        id: ID! @id
        users: [User] @relation(
            name: "UserRoles", link: TABLE, onDelete: SET_NULL
        )
    }
    """


@pytest.fixture(name="prev_schema_19")
def fixture_previous_schema_19():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        name: String!
    }
    """


@pytest.fixture(name="new_schema_19")
def fixture_new_schema_19():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        fullname: String! @db(rename: "full_name")
    }
    """


@pytest.fixture(name="prev_schema_20")
def fixture_previous_schema_20():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
    }
    """


@pytest.fixture(name="new_schema_20")
def fixture_new_schema_20():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }
    """


@pytest.fixture(name="prev_schema_21")
def fixture_previous_schema_21():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        role: UserRole! @default(value: ADMIN)
    }

    enum UserRole { ADMIN USER GUEST }
    """


@pytest.fixture(name="new_schema_21")
def fixture_new_schema_21():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        role: RoleUser @default(value: USER)
    }

    enum RoleUser { ADMIN USER GUEST }
    """


@pytest.fixture(name="prev_schema_22")
def fixture_previous_schema_22():
    """Fixture with previous GraphQL schema."""
    return """
    type User {
        id: ID! @id
        token: String!
        code: String! @unique
    }

    enum UserRole { ADMIN USER GUEST }
    """


@pytest.fixture(name="new_schema_22")
def fixture_new_schema_22():
    """Fixture with new GraphQL schema."""
    return """
    type User {
        id: ID! @id
        token: String! @unique
        code: String!
    }

    enum UserRole { ADMIN USER GUEST }
    """
