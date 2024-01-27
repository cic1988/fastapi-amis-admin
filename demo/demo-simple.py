from fastapi import FastAPI, Request
from fastapi_amis_admin.admin.admin import AdminApp

from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite

from fastapi_amis_admin.admin import admin
from fastapi_amis_admin.amis import components

from typing import Optional, Union

from fastapi_amis_admin.admin.admin import AdminApp, PageSchema, AmisAPI
from fastapi_amis_admin.amis.components import App, Page


class MultiPageAdmin(AdminApp):

    def get_page_schema(self) -> Optional[PageSchema]:
        if super().get_page_schema():
            self.page_schema.url = f"{self.router_path}{self.page_path}"
            self.page_schema.schemaApi = AmisAPI(
                method="post",
                url=f"{self.router_path}{self.page_path}",
                data={},
                cache=300000,
            )
        return self.page_schema

    async def get_page(self, request: Request) -> Union[Page, App]:
        page = Page(
            body=[{
                "type": 'button',
                "actionType": 'link',
                "link": '/admin/DocsAdminGroup/page/ChildPage?abc=1',
                "label": 'Jump to detail page',
                "level": 'primary'
            }]
        )
        return page

app = FastAPI()
site = AdminSite(settings=Settings(database_url_async="sqlite+aiosqlite:///amisadmin.db"))


class ChildChildPage(admin.PageAdmin):
    def get_page_schema(self) -> Optional[PageSchema]:
        schema = super().get_page_schema()
        schema.schemaApi = None
        
        schema.url = ":id"
        schema.schema_ = {
            "type": "page",
            "body": {
                "type": 'tpl',
                "className": 'text-red',
                "tpl": '<h1>页面url参数: id: ${params.id || "Not found"}</h1>'
            },
        }
        return schema

class ChildPage(admin.PageAdmin, admin.AdminGroup):
    def __init__(self, app: AdminApp):
        admin.PageAdmin.__init__(self, app)
        admin.AdminGroup.__init__(self, app)
        child = ChildChildPage(self)
        self.append_child(child)

    def get_page_schema(self) -> Optional[PageSchema]:
        schema = super().get_page_schema()
        schema.schemaApi = None
        schema.schema_ = {
            "type": "page",
            "body": [
                {
                    "type": 'button',
                    "actionType": 'link',
                    "link": f'{schema.url}/123',
                    "label": 'Go to child page',
                    "level": 'primary'
                }]
            }
        return schema


@site.register_admin
class HelloWorldPageAdmin(admin.PageAdmin):
    page_path = "/hello"
    page_schema = admin.PageSchema(
        type="page",
        label="Hello World"
    )
    page = components.Page(title='标题', body='Hello World!')

    def __init__(self, app: AdminApp):
        super().__init__(app)


@site.register_admin
class DocsAdminGroup(MultiPageAdmin):
    page_schema = admin.PageSchema(
        type="page",
        label="Docs"
    )
    page = components.Page(title='标题', body='Hello World!')

    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.register_admin(ChildPage)



site.mount_app(app)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
