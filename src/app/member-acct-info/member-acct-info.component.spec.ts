import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MemberAcctInfoComponent } from './member-acct-info.component';

describe('MemberAcctInfoComponent', () => {
  let component: MemberAcctInfoComponent;
  let fixture: ComponentFixture<MemberAcctInfoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MemberAcctInfoComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MemberAcctInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
