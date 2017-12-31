import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LocationMgmtComponent } from './location-mgmt.component';

describe('LocationMgmtComponent', () => {
  let component: LocationMgmtComponent;
  let fixture: ComponentFixture<LocationMgmtComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LocationMgmtComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LocationMgmtComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
