import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MgmtRolesPermsComponent } from './mgmt-roles-perms.component';

describe('MgmtRolesPermsComponent', () => {
  let component: MgmtRolesPermsComponent;
  let fixture: ComponentFixture<MgmtRolesPermsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MgmtRolesPermsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MgmtRolesPermsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
