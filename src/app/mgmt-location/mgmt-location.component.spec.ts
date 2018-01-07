import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MgmtLocationComponent } from './mgmt-location.component';

describe('MgmtLocationComponent', () => {
  let component: MgmtLocationComponent;
  let fixture: ComponentFixture<MgmtLocationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MgmtLocationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MgmtLocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
