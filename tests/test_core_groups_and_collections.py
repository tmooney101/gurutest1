
import json
import yaml
import unittest
import responses

from tests.util import use_guru, get_calls

import guru


class TestCore(unittest.TestCase):
  @use_guru()
  @responses.activate
  def test_get_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[])

    g.get_group("group name")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }])
  
  @use_guru()
  @responses.activate
  def test_get_collection_by_name(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "name": "test"
    }])
    collection = g.get_collection("test")
    self.assertEqual(collection.name, "test")
    self.assertEqual(collection.title, "test")

    # make sure title also works as an alias when setting its name.
    collection.title = "new title"
    self.assertEqual(collection.name, "new title")
    self.assertEqual(collection.title, "new title")

    self.assertEqual(get_calls(), [
      {
        "method": "GET",
        "url": "https://api.getguru.com/api/v1/collections"
      }
    ])

  @use_guru()
  @responses.activate
  def test_get_collection_by_id(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections/11111111-1111-1111-1111-111111111111", json={})
    g.get_collection("11111111-1111-1111-1111-111111111111")
    self.assertEqual(get_calls(), [
      {
        "method": "GET",
        "url": "https://api.getguru.com/api/v1/collections/11111111-1111-1111-1111-111111111111"
      }
    ])

  @use_guru()
  @responses.activate
  def test_make_collection(self, g):
    # make_collection() will look up the group by name so we need this to return something.
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "1234",
      "name": "All Members"
    }])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/collections", json={})
    g.make_collection("Test")

    self.assertEqual(get_calls(), [
      {
        "method": "GET",
        "url": "https://api.getguru.com/api/v1/groups"
      }, {
        "method": "POST",
        "url": "https://api.getguru.com/api/v1/collections",
        "body": {
          "name": "Test",
          "color": "#009688",
          "description": "",
          "collectionType": "INTERNAL",
          "publicCardsEnabled": True,
          "syncVerificationEnabled": False,
          "initialAdminGroupId": "1234"
        }
      }
    ])
  
  @use_guru()
  @responses.activate
  def test_make_collection_with_framework(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/frameworks", json=[{
      "id": "1234",
      "collection": {
        "color" : "#2962ff",
        "id" : "12345678-111a-222b-333c-87654321dcba",
        "description" : "Enable your team with: product FAQs, support processes, canned responses, tech stack tips, and more.\n",
        "slug" : "tjuii/Product-and-Process",
        "collectionType" : "INTERNAL",
        "name" : "Product & Process"
      }
    },{"id": "5678",
      "collection": {
        "color" : "#009688",
        "id" : "56781234-222b-111a-333c-dcba87654321",
        "description" : "This is just a test.\n",
        "slug" : "hynw9/Test",
        "collectionType" : "INTERNAL",
        "name" : "Test"
      }
    }])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/frameworks/import/1234", json={
      "color" : "#2962ff",
      "id" : "12345678-111a-222b-333c-87654321dcba",
      "description" : "Enable your team with: product FAQs, support processes, canned responses, tech stack tips, and more.\n",
      "slug" : "tjuii/Product-and-Process",
      "collectionType" : "INTERNAL",
      "name" : "Product & Process"
    })
    g.make_collection("Product & Process", use_framework=True)

    self.assertEqual(get_calls(), [
      {
        "method": "GET",
        "url": "https://api.getguru.com/api/v1/frameworks"
      }, {
        "method": "POST",
        "url": "https://api.getguru.com/api/v1/frameworks/import/1234"
      }
    ])

  @use_guru()
  @responses.activate
  def test_get_frameworks_then_make_collection_with_framework(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/frameworks", json=[{
      "id": "1234",
      "collection": {
        "color" : "#2962ff",
        "id" : "12345678-111a-222b-333c-87654321dcba",
        "description" : "Enable your team with: product FAQs, support processes, canned responses, tech stack tips, and more.\n",
        "slug" : "tjuii/Product-and-Process",
        "collectionType" : "INTERNAL",
        "name" : "Product & Process"
      }
    },{"id": "5678",
      "collection": {
        "color" : "#009688",
        "id" : "56781234-222b-111a-333c-dcba87654321",
        "description" : "This is just a test.\n",
        "slug" : "hynw9/Test",
        "collectionType" : "INTERNAL",
        "name" : "Test"
      }
    }])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/frameworks/import/1234", json={
      "color" : "#2962ff",
      "id" : "12345678-111a-222b-333c-87654321dcba",
      "description" : "Enable your team with: product FAQs, support processes, canned responses, tech stack tips, and more.\n",
      "slug" : "tjuii/Product-and-Process",
      "collectionType" : "INTERNAL",
      "name" : "Product & Process"
    })
    
    framework = g.get_framework("Product & Process")
    framework.import_framework()

    self.assertEqual(get_calls(), [
      {
        "method": "GET",
        "url": "https://api.getguru.com/api/v1/frameworks"
      }, {
        "method": "POST",
        "url": "https://api.getguru.com/api/v1/frameworks/import/1234"
      }
    ])

  @use_guru()
  @responses.activate
  def test_make_collection_with_invalid_color(self, g):
    with self.assertRaises(ValueError):
      g.make_collection("General", color="abc")
    with self.assertRaises(ValueError):
      g.make_collection("General", color="#12345")
    with self.assertRaises(ValueError):
      g.make_collection("General", color="123456")

  @use_guru()
  @responses.activate
  def test_make_collection_with_missing_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[])

    g.make_collection("Test")

    # this makes a GET call to look for the group called 'Test'
    # but it doesn't make the POST call because it doesn't find the group.
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }])
  
  @use_guru()
  @responses.activate
  def test_add_group_to_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "5678",
      "name": "Experts"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "abcd",
      "name": "General"
    }])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/collections/abcd/groups", json={})

    g.add_group_to_collection("Experts", "General", guru.AUTHOR)

    # this makes get calls to look up the group and collection by name, then
    # a post call to add the group to the collection.
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }, {
      "method": "POST",
      "url": "https://api.getguru.com/api/v1/collections/abcd/groups",
      "body": {
        "groupId": "5678",
        "role": "AUTHOR"
      }
    }])

  @use_guru()
  @responses.activate
  def test_add_group_to_collection_with_invalid_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "abcd",
      "name": "General"
    }])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/collections/abcd/groups", json={})

    result = g.add_group_to_collection("Experts", "General", guru.AUTHOR)

    self.assertEqual(result, False)
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }])
  
  @use_guru()
  @responses.activate
  def test_add_group_to_collection_with_invalid_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "1234",
      "name": "Experts"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/collections/abcd/groups", json={})

    result = g.add_group_to_collection("Experts", "General", guru.AUTHOR)

    self.assertEqual(result, False)
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }])

  @use_guru()
  @responses.activate
  def test_add_group_to_collection_when_its_already_on_it(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "5678",
      "name": "Experts"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "abcd",
      "name": "General"
    }])
    # when we try to add a group to a collection and it's already on the collection, the POST
    # call returns a 400 response, this will make us trigger a PUT call instead.
    responses.add(responses.POST, "https://api.getguru.com/api/v1/collections/abcd/groups", json={}, status=400)
    responses.add(responses.PUT, "https://api.getguru.com/api/v1/collections/abcd/groups/5678", json={})

    g.add_group_to_collection("Experts", "General", guru.AUTHOR)

    # this makes get calls to look up the group and collection by name, then
    # a post call to add the group to the collection.
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }, {
      "method": "POST",
      "url": "https://api.getguru.com/api/v1/collections/abcd/groups",
      "body": {
        "groupId": "5678",
        "role": "AUTHOR"
      }
    }, {
      "method": "PUT",
      "url": "https://api.getguru.com/api/v1/collections/abcd/groups/5678",
      "body": {
        "groupId": "5678",
        "role": "AUTHOR"
      }
    }])
  
  @use_guru()
  @responses.activate
  def test_remove_group_from_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "5678",
      "name": "Experts"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "abcd",
      "name": "General"
    }])
    responses.add(responses.DELETE, "https://api.getguru.com/api/v1/collections/abcd/groups/5678")

    g.remove_group_from_collection("Experts", "General")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }, {
      "method": "DELETE",
      "url": "https://api.getguru.com/api/v1/collections/abcd/groups/5678"
    }])
  
  @use_guru()
  @responses.activate
  def test_remove_group_from_collection_with_invalid_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "abcd",
      "name": "General"
    }])
    responses.add(responses.DELETE, "https://api.getguru.com/api/v1/collections/abcd/groups/5678")

    result = g.remove_group_from_collection("Experts", "General")

    self.assertEqual(result, False)
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }])
  
  @use_guru()
  @responses.activate
  def test_remove_group_from_collection_with_invalid_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "5678",
      "name": "Experts"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[])
    responses.add(responses.DELETE, "https://api.getguru.com/api/v1/collections/abcd/groups/5678")

    result = g.remove_group_from_collection("Experts", "General")

    self.assertEqual(result, False)
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }])

  @use_guru()
  @responses.activate
  def test_delete_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "abcd",
      "name": "General"
    }])
    responses.add(responses.DELETE, "https://api.getguru.com/api/v1/collections/abcd")

    g.delete_collection("General")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }, {
      "method": "DELETE",
      "url": "https://api.getguru.com/api/v1/collections/abcd"
    }])
  
  @use_guru()
  @responses.activate
  def test_delete_collection_with_invalid_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[])
    responses.add(responses.DELETE, "https://api.getguru.com/api/v1/collections/abcd")

    g.delete_collection("General")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }])

  @use_guru()
  @responses.activate
  def test_make_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[])
    responses.add(responses.POST, "https://api.getguru.com/api/v1/groups", json={})

    g.make_group("new group")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "POST",
      "url": "https://api.getguru.com/api/v1/groups",
      "body": {
        "id": "new-group",
        "name": "new group"
      }
    }])

  @use_guru()
  @responses.activate
  def test_make_group_with_duplicate_name(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "name": "new group"
    }])

    g.make_group("new group")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }])

  @use_guru()
  @responses.activate
  def test_get_group_members(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "name": "Experts",
      "id": "1111"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups/1111/members", json=[{
      "id": "user1@example.com",
      "dateCreated": "2019-10-04T19:04:12.108+0000",
      "user": {
        "status": "ACTIVE",
        "email": "user1@example.com",
        "firstName": "User",
        "lastName": "One"
      }
    }, {
      "id": "user2@example.com",
      "dateCreated": "2019-10-04T19:04:12.108+0000",
      "user": {
        "status": "ACTIVE",
        "email": "user2@example.com",
        "firstName": "User",
        "lastName": "Two"
      }
    }])

    users = g.get_group("Experts").get_members()

    self.assertEqual(users[0].last_name, "One")
    self.assertEqual(users[1].last_name, "Two")
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups/1111/members"
    }])

  @use_guru()
  @responses.activate
  def test_get_group_members_with_pagination(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "name": "Experts",
      "id": "2222"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups/2222/members", match_querystring=True, json=[
      {}, {}, {}, {}, {}
    ], headers={
      "Link": "< https://api.getguru.com/api/v1/groups/2222/members?token=1>"
    })
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups/2222/members?token=1", json=[
      {}, {}, {}, {}
    ], headers={
      "Link": "< https://api.getguru.com/api/v1/groups/2222/members?token=2>"
    })
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups/2222/members?token=2", json=[
      {}, {}
    ])

    users = g.get_group("Experts").get_members()

    self.assertEqual(len(users), 11)
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups/2222/members"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups/2222/members?token=1"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups/2222/members?token=2"
    }])

  @use_guru()
  @responses.activate
  def test_get_group_members_edge_cases(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "name": "Experts",
      "id": "1111"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups/1111/members", status=204)

    result1 = g.get_group_members("Doesn't Exist")
    result2 = g.get_group("Experts").get_members()

    self.assertEqual(result1, False)
    self.assertEqual(result2, [])
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups"
    }, {
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups/1111/members"
    }])

  @use_guru()
  @responses.activate
  def test_delete_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "1111",
      "name": "New Group"
    }])
    responses.add(responses.DELETE, "https://api.getguru.com/api/v1/groups/1111")

    g.delete_group("new group")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups",
    }, {
      "method": "DELETE",
      "url": "https://api.getguru.com/api/v1/groups/1111",
    }])

  @use_guru()
  @responses.activate
  def test_delete_invalid_group(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[])

    g.delete_group("new group")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/groups",
    }])

  @use_guru()
  @responses.activate
  def test_upload_content(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "1234",
      "name": "General"
    }])
    responses.add(responses.POST, "https://api.getguru.com/app/contentupload?collectionId=1234", json={})

    g.upload_content("General", "test.zip", "./tests/test.zip")

    post_body = get_calls()[1]["body"]
    self.assertEqual(b'Content-Disposition: form-data; name="contentFile"; filename="test.zip"\r\nContent-Type: application/zip\r\n\r\nzip file\r\n--' in post_body, True)
    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }, {
      "method": "POST",
      "url": "https://api.getguru.com/app/contentupload?collectionId=1234",
      "body": post_body
    }])

  @use_guru()
  @responses.activate
  def test_upload_and_get_error(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "1234",
      "name": "General"
    }])
    responses.add(responses.POST, "https://api.getguru.com/app/contentupload?collectionId=1234", status=400)

    with self.assertRaises(BaseException):
      g.upload_content("General", "test.zip", "./tests/test.zip")

  @use_guru()
  @responses.activate
  def test_upload_content_to_invalid_collection(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[])

    g.upload_content("General", "test.zip", "test.zip")

    self.assertEqual(get_calls(), [{
      "method": "GET",
      "url": "https://api.getguru.com/api/v1/collections"
    }])


  @use_guru()
  @responses.activate
  def test_get_object_by_reference(self, g):
    responses.add(responses.GET, "https://api.getguru.com/api/v1/collections", json=[{
      "id": "1111",
      "name": "General"
    }])
    responses.add(responses.GET, "https://api.getguru.com/api/v1/groups", json=[{
      "id": "2222",
      "name": "Experts"
    }])
    collection = g.get_collection("general")
    group = g.get_group("experts")

    collection2 = g.get_collection(collection)
    group2 = g.get_group(group)

    self.assertEqual(collection, collection2)
    self.assertEqual(group, group2)
