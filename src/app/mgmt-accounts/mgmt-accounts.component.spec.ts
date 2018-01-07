import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MgmtAccountsComponent } from './mgmt-accounts.component';

describe('MgmtAccountsComponent', () => {
  let component: MgmtAccountsComponent;
  let fixture: ComponentFixture<MgmtAccountsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MgmtAccountsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MgmtAccountsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
